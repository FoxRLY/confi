from dataclasses import MISSING, Field, fields, is_dataclass
from os import getenv
from types import UnionType
from typing import Annotated, Any, ClassVar, Type, TypeVar, Literal, Protocol, Union, get_args, get_origin


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]

def _camel_case_to_env(string: str) -> str:
    return "".join(["_" + char if char.isupper() else char.upper() for char in string]).lstrip("_")

def _snake_case_to_env(string: str) -> str:
    return string.upper()

def _boolean(value: str) -> bool | str:
    if value.lower() in ["true", "yes"]:
        return True
    elif value.lower() in ["false", "no"]:
        return False
    else:
        return value

T = TypeVar("T", bound=DataclassInstance)

def parse(cls: Type[T] ) -> T:
    """
    Спарсить переменные окружения с помощью указанного датакласса.

    Парсинг производится с учетом указанных в датаклассе полей.
    Можно указать три характеристики поля:
    1) Тип
    2) Дефолтное значение
    3) Модификатор

    Тип:
        - Обозначается как обычный тип (int), составной тип (int | float),
          набор строковых значений (Literal["read", "write"]),
          а также как вложенный датакласс (a: CustomDataClass).

        - Приведение строки-значения переменной к типу происходит
          в виде создания объекта из строки (field: FieldType => FieldType(str)).

        - При указании составного типа попытка приведения строки-значения идет
          по тому же порядку, в котором обозначены составные типы
          (float | int | str => 1: float(str), 2: int(str), 3: str(str)),
          заканчиваясь на первом успешном приведении.

        - Если значение не может быть приведено ни к одному из указанных типов,
          то значение остается в качестве строки (проблема решается модификаторами).

        - Вложенные датаклассы воспринимаются в качестве
          независимой цели парсинга переменных окружения, потому название поля
          не влияет на префикс (field: EnvVar => ENV_VAR, а не FIELD_ENV_VAR).

    Дефолтное значение:
        - Указывается обычными средствами датаклассов - через присваивание
          дефолтного значения или объекта field из модуля dataclasses
          (a: int = 10 или a: str = field(default_factory=lambda: "Привет")).

        - Дефолтные значения присваиваются только в том случае, если соответствующие
          переменные окружения не имеют значения.

        - Опциональные поля указываются через составной тип с None
          и присваивание дефолтным значением None (field: type | None = None).

    Модификатор:
        - Обозначается через тип Annotated с метаданными в качестве функций
          с одним аргументом и одним выходным значением
          (field: Annotated[int, lambda x: x + 10]).

        - Модификаторы не применяются к дефолтным значениям.

        - Модификаторы применяются после попытки привести строку-значение
          к типу и в том же порядке, в каком указаны внутри Annotated.

        - Модификаторы с выбросом исключений могут выступать в качестве фильтров.

    """
    # Префикс переменных для парсинга
    prefix = _camel_case_to_env(cls.__name__)

    # Словарь полей и их значений из окружения
    value_dict = dict()

    # Проходимся по каждому полю датакласса
    for class_field in fields(cls):
        field_types = [class_field.type]
        field_name = _snake_case_to_env(class_field.name)
        field_modificators = list()

        # Если тип - датакласс, то парсим его из окружения и вставляем в поле
        if is_dataclass(field_types[0]):
            value_dict[class_field.name] = parse(field_types[0]) # type: ignore
            continue

        # Если тип - набор строк, то добавляем фильтр
        if get_origin(field_types[0]) is Literal:
            possible_values = get_args(field_types[0])
            def literal_modificator(value):
                if value not in possible_values:
                    raise ValueError(f"Ошибка: переменная {prefix}_{field_name} должна принимать одно из этих значений: {possible_values}")
                return value

            field_modificators.append(literal_modificator)
            field_types = [str]

        # Если тип имеет модификаторы, то собираем их в список
        if get_origin(field_types[0]) is Annotated:
            args = get_args(field_types[0])
            field_types = [args[0]]
            field_modificators += args[1:]

        # Если тип составной, то переводим его в список типов
        if get_origin(field_types[0]) in (Union, UnionType):
            field_types = list(get_args(field_types[0]))

        # Получаем строковое значение из окружения
        initial_value = getenv(f"{prefix}_{field_name}")
        value = initial_value

        # Если значения нет
        if value is None:
            # И нет дефолтных значений для поля, то выдаем ошибку
            if class_field.default is MISSING and class_field.default_factory is MISSING:
                raise ValueError(f"Ошибка: переменная {prefix}_{field_name} не найдена и не имеет значения по умолчанию")
            # Иначе пропускаем поле, автоматом присваивая ему дефолтное значение
            continue

        # Попытка преобразовать поле в нужные типы
        for field_type in field_types:
            try:
                if field_type is bool:
                    field_type = _boolean
                value = field_type(value) # type: ignore
                break
            except:
                continue

        # Добавление модификатора проверки типа в конец
        def enforce_type_modificator(value):
            if type(value) not in field_types:
                raise ValueError(f"Ошибка: поле {cls.__name__}.{class_field.name} c типами {field_types} не может принять значение {type(value)}({value})")
            return value
        field_modificators.append(enforce_type_modificator)

        # Применение модификаторов
        for modificator in field_modificators:
            try:
                value = modificator(value)
            except Exception as e:
                raise ValueError(f"Ошибка: {cls.__name__}.{class_field.name} | {modificator.__name__}: {e}")

        # Сохранение значения поля
        value_dict[class_field.name] = value

    # Создание объекта из полученных полей и их значений
    return cls(**value_dict)

