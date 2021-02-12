from typing import Any, Optional, Union, List, Dict, TypeVar, Generic, Sequence, Callable, Tuple, Set, Sequence
from typing_extensions import Protocol
from .elements import ClauseElement as ClauseElement, ColumnElement
from .base import Executable as Executable, SchemaVisitor as SchemaVisitor
from .schema import Table, MetaData, SchemaItem, ForeignKeyConstraint, ForeignKey
from .compiler import IdentifierPreparer
from .type_api import TypeEngine
from ..engine import Dialect, Engine, Connection, ResultProxy, Connectable

_T = TypeVar('_T')

class _DDLCompiles(ClauseElement): ...

class _DDLCallable(Protocol):
    def __call__(self, ddl: DDLElement, target: Optional[Union[Table, MetaData]], bind: Connection,
                 tables: Optional[List[Any]] = ..., state: Optional[Any] = ...,
                 checkfirst: bool = ...) -> bool: ...

class _DDLOnCallback(Protocol):
    def __call__(self, ddl: DDLElement, event: Optional[str], target: Optional[Union[Table, MetaData]],
                 connection: Connection, tables: Optional[List[Any]] = ...) -> bool: ...

_DDLE = TypeVar('_DDLE', bound=DDLElement)

class DDLElement(Executable, _DDLCompiles):
    target: Optional[SchemaItem] = ...
    on: Optional[Union[str, Tuple[str, ...], _DDLOnCallback]] = ...
    dialect: Optional[Dialect] = ...
    callable_: Optional[_DDLCallable] = ...
    bind: Optional[Union[Engine, Connection]] = ...
    def execute(self, bind: Optional[Union[Engine, Connection]] = ...,  # type: ignore  # incompatible with Executable.execute
                target: Optional[SchemaItem] = ...) -> Optional[ResultProxy]: ...
    def execute_at(self, event_name: str, target: SchemaItem) -> None: ...
    def against(self: _DDLE, target: SchemaItem) -> _DDLE: ...
    state: Any = ...
    def execute_if(self: _DDLE, dialect: Optional[Union[str, Sequence[str]]] = ..., callable_: Optional[_DDLCallable] = ...,
                   state: Optional[Any] = ...) -> _DDLE: ...
    def __call__(self, target: Optional[Union[Table, MetaData]], bind: Connection, **kw: Any) -> Optional[ResultProxy]: ...

class DDL(DDLElement):
    __visit_name__: str = ...
    statement: str = ...
    context: Dict[Any, Any] = ...
    on: Optional[Union[str, Tuple[str, ...], _DDLOnCallback]] = ...
    def __init__(self, statement: str, on: Optional[Union[str, Tuple[str, ...], _DDLOnCallback]] = ...,
                 context: Optional[Dict[Any, Any]] = ..., bind: Optional[Connectable] = ...) -> None: ...

class _CreateDropBase(DDLElement, Generic[_T]):
    element: _T = ...
    bind: Optional[Connection] = ...
    def __init__(self, element: _T, on: Optional[Union[str, Tuple[str, ...], _DDLOnCallback]] = ...,
                 bind: Optional[Connection] = ...) -> None: ...

class CreateSchema(_CreateDropBase[str]):
    __visit_name__: str = ...
    quote: Any = ...
    def __init__(self, name: str, quote: Optional[Any] = ..., **kw) -> None: ...

class DropSchema(_CreateDropBase[str]):
    __visit_name__: str = ...
    quote: Any = ...
    cascade: bool = ...
    def __init__(self, name: str, quote: Optional[Any] = ..., cascade: bool = ..., **kw) -> None: ...

class CreateTable(_CreateDropBase[Table]):
    __visit_name__: str = ...
    columns: List[CreateColumn[Any]] = ...
    include_foreign_key_constraints: Optional[Sequence[ForeignKeyConstraint]] = ...
    def __init__(self, element: Table, on: Optional[Union[str, Tuple[str, ...], _DDLOnCallback]] = ...,
                 bind: Optional[Connectable] = ...,
                 include_foreign_key_constraints: Optional[Sequence[ForeignKeyConstraint]] = ...) -> None: ...

class _DropView(_CreateDropBase[str]):
    __visit_name__: str = ...

class CreateColumn(_DDLCompiles, Generic[_T]):
    __visit_name__: str = ...
    element: ColumnElement[_T] = ...
    def __init__(self, element: ColumnElement[_T]) -> None: ...

class DropTable(_CreateDropBase[str]):
    __visit_name__: str = ...

class CreateSequence(_CreateDropBase[str]):
    __visit_name__: str = ...

class DropSequence(_CreateDropBase[str]):
    __visit_name__: str = ...

class CreateIndex(_CreateDropBase[str]):
    __visit_name__: str = ...

class DropIndex(_CreateDropBase[str]):
    __visit_name__: str = ...

class AddConstraint(_CreateDropBase[str]):
    __visit_name__: str = ...
    def __init__(self, element: str, *args: Any, **kw: Any) -> None: ...

class DropConstraint(_CreateDropBase[str]):
    __visit_name__: str = ...
    cascade: bool = ...
    def __init__(self, element: str, cascade: bool = ..., **kw: Any) -> None: ...

class DDLBase(SchemaVisitor):
    connection: Connection = ...
    def __init__(self, connection: Connection) -> None: ...

class SchemaGenerator(DDLBase):
    checkfirst: bool = ...
    tables: Optional[List[Table]] = ...
    preparer: IdentifierPreparer = ...
    dialect: Dialect = ...
    memo: Dict[Any, Any] = ...
    def __init__(self, dialect: Dialect, connection: Connection, checkfirst: bool = ...,
                 tables: Optional[List[Table]] = ..., **kwargs: Any) -> None: ...
    def visit_metadata(self, metadata: MetaData) -> None: ...
    def visit_table(self, table: Table, create_ok: bool = ...,
                    include_foreign_key_constraints: Optional[Sequence[ForeignKeyConstraint]] = ...,
                    _is_metadata_operation: bool = ...) -> None: ...
    def visit_foreign_key_constraint(self, constraint: ForeignKeyConstraint) -> None: ...
    def visit_sequence(self, sequence: str, create_ok: bool = ...): ...
    def visit_index(self, index: str) -> None: ...

class SchemaDropper(DDLBase):
    checkfirst: bool = ...
    tables: Optional[List[Table]] = ...
    preparer: IdentifierPreparer = ...
    dialect: Dialect = ...
    memo: Dict[Any, Any] = ...
    def __init__(self, dialect: Dialect, connection: Connection, checkfirst: bool = ...,
                 tables: Optional[List[Table]] = ..., **kwargs: Any) -> None: ...
    def visit_metadata(self, metadata: MetaData) -> None: ...
    def visit_index(self, index: str) -> None: ...
    def visit_table(self, table: Table, drop_ok: bool = ..., _is_metadata_operation: bool = ...) -> None: ...
    def visit_foreign_key_constraint(self, constraint: ForeignKeyConstraint) -> None: ...
    def visit_sequence(self, sequence: str, drop_ok: bool = ...) -> None: ...

def sort_tables(tables: Sequence[Table], skip_fn: Optional[Callable[[ForeignKey], bool]] = ...,
                extra_dependencies: Optional[Sequence[Tuple[Table, Table]]] = ...) -> List[Table]: ...


_SortResultType = List[Tuple[Optional[Table], Union[Set[ForeignKeyConstraint], List[ForeignKeyConstraint]]]]

def sort_tables_and_constraints(tables: Sequence[Table],
                                filter_fn: Optional[Callable[[ForeignKeyConstraint], Optional[bool]]] = ...,
                                extra_dependencies: Optional[Sequence[Tuple[Table, Table]]] = ...) -> _SortResultType: ...
