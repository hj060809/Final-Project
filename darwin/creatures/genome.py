from typing import Any, ClassVar, Iterable, Self, TYPE_CHECKING
import numpy as np
from dataclasses import dataclass, replace

if TYPE_CHECKING:
    from .body import Body
    from .brain import Brain
    from .sensor import Sensor

STD_CONSTRAINT_RATIO = 10.0

"""
STD의 범위는 REF_VAL에 무관하게 같다
-> 점차 std가 줄어들 
"""

@dataclass(frozen=True)
class GeneUnit:
    """각 Gene을 결정하는 스칼라 1개"""
    name: str
    refVal: float
    std: float
    baseStd: float   # 이 형질의 기준 변이 폭. 변이해도 바뀌지 않음

    @classmethod
    def fromValue(cls, name: str, value: float, std: float) -> Self:
        return cls(name=name, refVal=value, std=std, baseStd=std)

    def __mul__(self, other):
        return self.crossover(other)

    def express(self) -> float:
        return self.refVal

    def mutate(self, temperature: float) -> Self:
        newStd = float(np.clip(
            self.std * np.exp(temperature * np.random.randn()),
            self.baseStd / STD_CONSTRAINT_RATIO,
            self.baseStd * STD_CONSTRAINT_RATIO,
        ))
        newRef = self.refVal + newStd * np.random.randn()
        return replace(self, refVal=newRef, std=newStd)

    def crossover(self, other: Self) -> Self:
        if type(self) is not type(other) or self.name != other.name:
            raise ValueError(f'cannot cross unit {self.name!r} with {other.name!r}')
        return self if np.random.rand() < 0.5 else other

@dataclass(frozen=True)
class UnitSpec:
    name: str
    initValue: float                    # 표현형 단위 (사람이 읽는 값)
    initStd: float                      # 잠재 공간 단위
    unitType: type[GeneUnit] = GeneUnit

    def sample(self) -> GeneUnit:
        unit = self.unitType.fromValue(self.name, self.initValue, self.initStd)
        return replace(unit, refVal=unit.refVal + self.initStd * np.random.randn())
    
class Gene[P]:
    """
    Sensor, Brain 등 부품 1개를 결정하는 유전자, 추상 클래스
    **SCHEMA는 PRODUCT의 __init__ 입력과 같아야 합니다**
    """
    _catalog: ClassVar[list[type[Gene]]]
    SCHEMA: ClassVar[tuple[UnitSpec, ...]] = ()
    PRODUCT: ClassVar[type]          # 이 Gene이 만들어 낼 부품 클래스

    def __init__(self, units: tuple[GeneUnit, ...]):
        names = tuple(u.name for u in units)
        expected = tuple(spec.name for spec in self.SCHEMA)

        if names != expected:
            raise ValueError(f'{type(self).__name__} expects {self.SCHEMA}, got {names}')
        
        self._units = tuple(units)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if Gene in cls.__bases__:            # 범주 클래스: 자기 카탈로그 생성
            cls._catalog = []
        elif 'PRODUCT' in cls.__dict__:      # 구체 클래스: 소속 범주에 등록
            cls._catalog.append(cls)

    def __mul__(self, other):
        return self.crossover(other)

    @classmethod
    def getCatalog(cls) -> tuple[type[Self], ...]:
        return tuple(cls._catalog)

    @classmethod
    def init(cls, units: Iterable[GeneUnit] = ()):
        specs = {spec.name: spec for spec in cls.SCHEMA}

        given: dict[str, GeneUnit] = {}
        for u in units:
            if u.name not in specs:
                raise ValueError(f'{type(cls).__name__} has no unit {u.name!r}')
            if u.name in given:
                raise ValueError(f'duplicate unit: {u.name!r}')
            if type(u) is not specs[u.name].unitType:
                raise TypeError(
                    f'{u.name!r} expects {specs[u.name].unitType.__name__}, got {type(u).__name__}'
                )
            given[u.name] = u

        return cls(units=tuple(
            given[spec.name] if spec.name in given else spec.sample()
            for spec in cls.SCHEMA
        ))

    @classmethod
    def sample(cls) -> Self:
        return cls(tuple(spec.sample() for spec in cls.SCHEMA))

    def crossover(self, other: Self) -> Self:
        if type(self) is not type(other):
            raise TypeError(f'cannot cross {type(self).__name__} with {type(other).__name__}')
        
        return type(self)(tuple(
            mine.crossover(theirs)
            for mine, theirs in zip(self._units, other._units, strict=True)
        ))

    def mutate(self, temperature: float) -> Self:
        return type(self)(tuple(u.mutate(temperature) for u in self._units))

    def values(self) -> dict[str, float]:
        return {u.name: u.express() for u in self._units}

    def express(self, **deps) -> P:
        """deps를 통해 Gene으로 결정되지 않는 요소를 입력 가능"""
        return self.PRODUCT(**self.values(), **deps)

class SensorGene(Gene['Sensor']): pass
class BrainGene(Gene['Brain']): pass
class BodyGene(Gene['Body']): pass

@dataclass(frozen=True)
class PositiveUnit(GeneUnit):
    """express()의 결과가 linear 스케일의 양수로 고정됩니다."""
    def express(self) -> float:
        z = super().express()
        return (z+np.sqrt(z**2 + 4))/2

    @classmethod
    def fromValue(cls, name: str, refVal: float, std: float) -> Self:
        if refVal <= 0:
            raise ValueError(f'{name}: refVal must be bigger than 0, got {refVal}')
        return cls(name=name, refVal=refVal-1/refVal, std=std, baseStd=std)


@dataclass(frozen=True)
class ProbUnit(GeneUnit):
    """express()의 결과가 0~1로 고정됩니다."""
    def express(self) -> float:
        return float(1 / (1 + np.exp(-np.clip(super().express(), -50, 50))))

    @classmethod
    def fromValue(cls, name: str, p: float, std: float) -> Self:
        if not 0.0 < p < 1.0:
            raise ValueError(f'{name}: p must be in (0, 1), got {p}')
        return cls(name=name, refVal=float(np.log(p / (1 - p))), std=std, baseStd=std)

@dataclass(frozen=True)
class ActivenessPair[P]:
    """Gene과 그 활성도"""
    gene: Gene[P]
    activeness: ProbUnit

    @property
    def kind(self) -> type[Gene[P]]:
        return type(self.gene)
    
    def __mul__(self, other):
        return self.crossover(other)

    def isActive(self) -> bool:
        return self.activeness.express() > 0.5

    def crossover(self, other: Self) -> Self:
        return type(self)(self.gene * other.gene, self.activeness * other.activeness)

    def mutate(self, temperature: float) -> Self:
        return type(self)(self.gene.mutate(temperature), self.activeness.mutate(temperature))

class GeneContainer[P]:
    def __init__(self, elements: Iterable[ActivenessPair[P]]):
        self._elements: dict[type[Gene[P]], ActivenessPair[P]] = {}
        for pair in elements:
            if pair.kind in self._elements:
                raise ValueError(f'duplicate gene: {pair.kind.__name__}')
            self._elements[pair.kind] = pair

    @classmethod
    def init(cls, initGenes: Iterable[Gene[P]], catalog: Iterable[type[Gene[P]]], initStd: float = 1.0) -> Self:
        catalog = tuple(catalog)
        initGenes = tuple(initGenes)

        missing = [type(g).__name__ for g in initGenes if type(g) not in catalog]
        if missing:
            raise ValueError(f'not in catalog: {missing}')
        
        given: dict[type[Gene[P]], Gene[P]] = {}
        for g in initGenes:
            kind = type(g)
            if kind not in catalog:
                raise ValueError(f'{kind.__name__} is not in catalog')
            if kind in given:
                raise ValueError(f'duplicate gene: {kind.__name__}')
            given[kind] = g

        pairs: list[ActivenessPair[P]] = []
        for kind in catalog:
            activeness = ProbUnit.fromValue(
                name=f'activeness({kind.__name__})',
                p=(0.9 if kind in given else 0.1),
                std=initStd
            )
            gene = given[kind] if kind in given else kind.sample()
            pairs.append(ActivenessPair(gene, activeness))

        return cls(pairs)

    def __mul__(self, other) -> Self:
        return self.crossover(other)

    def crossover(self, other: Self) -> Self:
        if self._elements.keys() != other._elements.keys():
            raise ValueError('cannot cross containers with different catalogs')
        return type(self)(
            self._elements[k]*other._elements[k] for k in self._elements
        )

    def mutate(self, temperature: float) -> Self:
        return type(self)(pair.mutate(temperature) for pair in self._elements.values())

    def actives(self) -> list[Gene[P]]:
        return [pair.gene for pair in self._elements.values() if pair.isActive()]

    def express(self) -> tuple[P, ...]:
        return tuple(pair.gene.express() for pair in self._elements.values() if pair.isActive())

@dataclass(frozen=True)
class Phenotype:
    body: Body
    sensors: tuple[Sensor, ...]
    brain: Brain

class Genome:
    """한 Creature를 구성하는 전체 유전체 지도"""
    def __init__(
        self,
        bodyGene: BodyGene,
        brainGene: BrainGene,
        sensorGenes: GeneContainer[Sensor]
    ):
        self._bodyGene = bodyGene
        self._brainGene = brainGene
        self._sensorGenes = sensorGenes

    @classmethod
    def init(
        cls,
        bodyGene: BodyGene,
        brainGene: BrainGene,
        sensorGenes: Iterable[SensorGene],
        sensorGenePool: Iterable[type[SensorGene]] | None = None,
    ) -> Genome:
        pool = SensorGene.getCatalog() if sensorGenePool is None else sensorGenePool
        return Genome(
            bodyGene = bodyGene,
            brainGene = brainGene,
            sensorGenes = GeneContainer.init(
                initGenes=sensorGenes,
                catalog=pool
            )
        )

    def __mul__(self, other: Genome) -> Genome:
        return self.crossover(other)

    def crossover(self, other: Genome) -> Genome:
        return Genome(
            bodyGene=self._bodyGene*other._bodyGene,
            brainGene=self._brainGene*other._brainGene,
            sensorGenes=self._sensorGenes*other._sensorGenes
        )

    def mutate(self, temperature: float = 0.2) -> Genome:
        return Genome(
            bodyGene=self._bodyGene.mutate(temperature),
            brainGene=self._brainGene.mutate(temperature),
            sensorGenes=self._sensorGenes.mutate(temperature)
        )

    def distance(self, other: Genome):
        pass

    def express(
            self,
            bodyDeps: dict[str, Any] = {},
            brainDeps: dict[str, Any] = {},
        ):
        return Phenotype(
            body=self._bodyGene.express(**bodyDeps),
            brain=self._brainGene.express(**brainDeps),
            sensors=self._sensorGenes.express()
        )