from unittest.mock import MagicMock, AsyncMock
from unittest import mock
import pytest
from peewee import SqliteDatabase
from telegram import Update, User, Message, Chat


from nice_bot.db_init import PidorStickers, Members, Stats, PidorStats, CurrentPidor, CurrentNice
from nice_bot.run import (get_stickers_enable, create_user, unreg_in_data, update_pidor_stats,
                          unreg, reg, get_all_members,get_random_id, get_user_coefficient,
                          get_random_id_carmic,check_coefficient_for_chosen)

@pytest.fixture
def fake_update():
    user = User(id=435466570, first_name='Test', is_bot=False)
    chat = Chat(id=457200309, type='group')
    message = Message(message_id=1, date=None, chat=chat, from_user=user, text='Тестовое сообщение')
    return Update(update_id=1, message=message)

@pytest.fixture
def fake_context():
    #user = User(id=435466570, first_name='Test', is_bot=False)
    #chat = Chat(id=457200309, type='group')
    #context = AsyncMock()
    #context.bot.send_message = AsyncMock()
    #context.bot.get_chat_member =
    #member = User(first_name='Vladimir', id=127637491, is_bot=False, is_premium=True, language_code='ru', username='drop1234567')
    user = User(id=435466570, first_name='Test', is_bot=False)
    chat = Chat(id=457200309, type='group')
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.get_chat_member = AsyncMock()  # Исп

    #return context(user=member)
    return context


@pytest.fixture
def fake_update_run():
    user = User(id=12345, first_name='Test', is_bot=False)
    chat = Chat(id=12345, type='group')
    message = Message(message_id=1, date=None, chat=chat, from_user=user, text='Тестовое сообщение')
    return Update(update_id=1, message=message)

@pytest.fixture
def fake_context_run():
    #user = User(id=435466570, first_name='Test', is_bot=False)
    #chat = Chat(id=457200309, type='group')
    #context = AsyncMock()
    #context.bot.send_message = AsyncMock()
    #context.bot.get_chat_member =
    #member = User(first_name='Vladimir', id=127637491, is_bot=False, is_premium=True, language_code='ru', username='drop1234567')
    user = User(id=12345, first_name='Test', is_bot=False)
    chat = Chat(id=12345, type='group')
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.get_chat_member = AsyncMock()  # Исп

    #return context(user=member)
    return context

@pytest.fixture(scope='module')
def setup_database():
    # Создание экземпляра тестовой базы данных
    test_db = SqliteDatabase(':memory:')

    # Связывание моделей с тестовой базой данных
    PidorStickers._meta.database = test_db
    Members._meta.database = test_db

    test_db.bind([PidorStickers, Members, Stats, PidorStats, CurrentPidor,CurrentNice], bind_refs=False, bind_backrefs=False)
    #test_db.bind([Members], bind_refs=False, bind_backrefs=False)

    # Создание таблиц в тестовой базе данных
    test_db.connect(reuse_if_open=True)  # Используйте reuse_if_open=True для предотвращения ошибок
    test_db.create_tables([PidorStickers, Members, Stats, PidorStats, CurrentPidor, CurrentNice])

    yield  # Здесь тесты будут выполняться

    # Закрытие соединения и очистка базы данных после тестов
    test_db.drop_tables([PidorStickers, Members, Stats, PidorStats, CurrentPidor, CurrentNice])
    test_db.close()

# Использование mock.patch для имитации подключения к базе данных
@mock.patch('nice_bot.run.dbhandle.connect')
def test_get_stickers_enable(mock_connect, setup_database):
    # Имитация подключения к базе данных
    mock_connect.return_value = setup_database

    # Предполагаем, что chat_id 123 существует и у него включены стикеры
    chat_id = 123
    PidorStickers.create(chat_id=chat_id, enable=True)
    assert get_stickers_enable(chat_id) == True

    # Предполагаем, что chat_id 321 существует и у него выключены стикеры
    chat_id = 321
    PidorStickers.create(chat_id=chat_id, enable=False)
    assert get_stickers_enable(chat_id) == False
@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_unreg_in_data(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database
    assert unreg_in_data(123, 123) == 'Пользователь не найден'

    Members.create(chat_id=123,
    member_id=123,
    coefficient=10,
    pidor_coefficient=10,
    full_name='test',
    nick_name='test')

    assert unreg_in_data(123, 123) == 'deleted'

@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_update_pidor_stats(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    Stats.create(chat_id=123,
    member_id=123,
    count=1)

    assert update_pidor_stats(123, 123, 'stats') == 2
    #assert update_pidor_stats(123, 123, 'pidor_stats') == None

@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
@pytest.mark.asyncio
async def test_unreg(mock_connect, mock_close, setup_database, fake_update, fake_context):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database
    await unreg(update=fake_update, context=fake_context)

    assert fake_context.bot.send_message.called == True

    Members.create(chat_id=457200309,
                   member_id=435466570,
                   coefficient=10,
                   pidor_coefficient=10,
                   full_name='test',
                   nick_name='test')

    await unreg(update=fake_update, context=fake_context)

    assert fake_context.bot.send_message.called == True

   # Members.create(chat_id=,
    #member_id=435466570,
    #coefficient=,
    #pidor_coefficient=,
    #full_name='Test',
    #nick_name='Test')

    #await unreg(update=fake_update, context=fake_context)

@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
@pytest.mark.asyncio
async def test_reg(mock_connect, mock_close, setup_database, fake_update_run, fake_context_run):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    await reg(update=fake_update_run, context=fake_context_run)
    assert fake_context_run.bot.send_message.called

    await reg(update=fake_update_run, context=fake_context_run)
    assert fake_context_run.bot.send_message.called



@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_create_user(mock_connect, mock_close, setup_database, fake_update_run, fake_context_run):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    assert create_user(500, 5001, 'testing', 'testing') == True
    #await reg(update=fake_update_run, context=fake_context_run)
    #assert fake_context_run.bot.send_message.called


@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_get_all_members(mock_connect, mock_close, setup_database, fake_update_run, fake_context_run):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    Members.create(chat_id=123456,
    member_id=123456,
    coefficient=10,
    pidor_coefficient=10,
    full_name='test',
    nick_name='test')

    assert get_all_members(123456) == [123456]
    #await reg(update=fake_update_run, context=fake_context_run)
    #assert fake_context_run.bot.send_message.called


@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_get_random_id(mock_connect, mock_close, setup_database, fake_update_run, fake_context_run):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    Members.create(chat_id=991,
                   member_id=991,
                   coefficient=10,
                   pidor_coefficient=10,
                   full_name='test',
                   nick_name='test')
    Members.create(chat_id=992,
                   member_id=992,
                   coefficient=10,
                   pidor_coefficient=10,
                   full_name='test',
                   nick_name='test')

    assert get_random_id(991, 'nice')
    assert get_random_id(992, 'pidor')
    assert get_random_id(993, 'Nothing')
    #await reg(update=fake_update_run, context=fake_context_run)
    #assert fake_context_run.bot.send_message.called


@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_get_user_coefficient(mock_connect, mock_close, setup_database, fake_update_run, fake_context_run):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    Members.create(chat_id=551,
                   member_id=551,
                   coefficient=10,
                   pidor_coefficient=10,
                   full_name='test',
                   nick_name='test')

    assert get_user_coefficient(551, 551,'nice') == 10
    assert get_user_coefficient(551, 551, 'pidor') == 10


def test_check_coefficient_for_chosen():
    assert check_coefficient_for_chosen(10) == 10
    assert check_coefficient_for_chosen(0) == 0
    assert check_coefficient_for_chosen(21) == 21







# Очистка данных после теста
# @pytest.fixture(autouse=True)
# def teardown_function():
#     yield
#     test_db.execute_sql('PRAGMA foreign_keys=OFF;')
#     test_db.drop_tables([PidorStickers])
#     test_db.execute_sql('PRAGMA foreign_keys=ON;')
#     test_db.close()



