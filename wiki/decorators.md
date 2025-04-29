## Обзор

Декораторы предоставляют удобный способ регистрации обработчиков с дополнительными метаданными. Они заменяют старый подход с префиксами в именах функций (`_cmd_`, `_botcmd_` и т.д.).

## Доступные декораторы

### `@command`

Регистрирует команду с префиксом (из конфига)

```
@command(
    aliases: List[str] = None,
    description: Dict[str, str] = None
)
```

**Параметры:**

- `aliases` - список альтернативных названий команды
    
- `description` - локализованные описания (ключи - языковые коды)
    

**Пример:**
```
@command(aliases=['p', 'ping'], description={
    "ru": "Проверка задержки бота", 
    "en": "Check bot latency"
})
async def ping(self, message: types.Message):
    """Дополнительное описание для help-команд"""
    await message.answer("Pong!")
```
---

### `@bot_command`

Регистрирует команду бота (начинается с /)
```
@bot_command(
    aliases: List[str] = None,
    description: Dict[str, str] = None
)
```
**Пример:**
```
@bot_command(description={"ru": "Начать работу", "en": "Start conversation"})
async def start(self, message: types.Message):
    await message.answer("Добро пожаловать!")
```
---

### `@inline_command`

Регистрирует inline-команду (через @бот)
```
@inline_command(
    aliases: List[str] = None,
    description: Dict[str, str] = None
)
```
**Пример:**
```
@inline_command(aliases=['wiki'])
async def search(self, query: types.InlineQuery):
    await query.answer(...)
```
---

### `@inline`

Регистрирует обработчик всех inline-запросов

@inline(description: Dict[str, str] = None)

**Пример:**
```
@inline(description={"ru": "Поиск по базе", "en": "Database search"})
async def handle_inline(self, query: types.InlineQuery):
    pass
```
---

### `@bot_message`

Регистрирует обработчик обычных сообщений боту
```
@bot_message(description: Dict[str, str] = None)
```
---

### `@callback_query`

Регистрирует обработчик callback-кнопок
```
@callback_query(description: Dict[str, str] = None)
```
**Пример:**
```
@callback_query()
async def handle_button(self, call: types.CallbackQuery):
    await call.answer()
```
---

### `@business_message`

Регистрирует обработчик бизнес-сообщений
```
@business_message(description: Dict[str, str] = None)
```
---

### `@edited_business_message`

Регистрирует обработчик измененных бизнес-сообщений
```
@edited_business_message(description: Dict[str, str] = None)
```
---

### `@deleted_business_message`

Регистрирует обработчик удаленных бизнес-сообщений
```
@deleted_business_message(description: Dict[str, str] = None)
```
## Особенности использования

1. **Импорт декораторов**:
    ```
    from tensai.decorators import command, bot_command, callback_query
    ```
2. **Совместимость**:
    
    - Старый стиль с префиксами (`_cmd_`, `_botcmd_`) продолжает работать
        
    - Можно комбинировать оба подхода
        
3. **Локализация**:
    ```
    @command(description={
        "ru": "Русское описание",
        "en": "English description",
        "es": "Descripción en español"
    })
    ```
4. **Документация**:
    
    - Декораторы поддерживают обычные docstrings
        
    - Описание из декоратора имеет приоритет над docstring
        

## Пример модуля с декораторами
```
from aiogram import types
from tensai.decorators import command, bot_command, callback_query
from tensai import Module

class ExampleModule(Module):
    strings = {
        "ru": {"hello": "Привет, {name}!"},
        "en": {"hello": "Hello, {name}!"}
    }

    @command(aliases=['hi'], description={
        "ru": "Приветствие пользователя",
        "en": "Greet the user"
    })
    async def hello(self, message: types.Message):
        """Альтернативное описание команды"""
        name = message.from_user.full_name
        await message.answer(self.strings('hello').format(name=name))

    @bot_command()
    async def start(self, message: types.Message):
        await message.answer("Добро пожаловать!")

    @callback_query()
    async def on_button_click(self, call: types.CallbackQuery):
        await call.answer("Кнопка нажата!")
```
## Миграция со старого формата

Старый стиль:
```
async def _cmd_ping(self, message: types.Message):
    pass
```
Новый стиль:
```
@command(aliases=['p'])
async def ping(self, message: types.Message):
    pass
```
