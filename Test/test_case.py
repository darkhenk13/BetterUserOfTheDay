from unittest.mock import MagicMock, AsyncMock
from unittest import mock
import pytest
from peewee import SqliteDatabase
from telegram import Update, User, Message, Chat


from nice_bot.db_init import PidorStickers, Members, Stats, PidorStats, CurrentPidor, CurrentNice, CarmicDicesEnabled
from nice_bot.run import (get_stickers_enable, create_user, unreg_in_data, update_pidor_stats,
                          unreg, reg, get_all_members,get_random_id, get_user_coefficient,
                          get_random_id_carmic,check_coefficient_for_chosen,check_coefficient_for_others,
                          update_coefficient_for_users, get_pidor_stats, get_user_percentage_nice_pidor,
                          reset_stats_data, update_current, is_not_time_expired,add_chat_to_carmic_dices_in_db,
                          remove_chat_from_carmic_dices_in_db, get_current_user, set_full_name_and_nickname_in_db,
                          get_full_name_from_db,get_nickname_from_db)

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

    test_db.bind([PidorStickers, Members, Stats, PidorStats, CurrentPidor,CurrentNice,CarmicDicesEnabled], bind_refs=False, bind_backrefs=False)
    #test_db.bind([Members], bind_refs=False, bind_backrefs=False)

    # Создание таблиц в тестовой базе данных
    test_db.connect(reuse_if_open=True)  # Используйте reuse_if_open=True для предотвращения ошибок
    test_db.create_tables([PidorStickers, Members, Stats, PidorStats, CurrentPidor, CurrentNice,CarmicDicesEnabled])

    yield  # Здесь тесты будут выполняться

    # Закрытие соединения и очистка базы данных после тестов
    test_db.drop_tables([PidorStickers, Members, Stats, PidorStats, CurrentPidor, CurrentNice,CarmicDicesEnabled])
    test_db.close()

# Использование mock.patch для имитации подключения к базе данных
@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_get_stickers_enable(mock_connect, mock_close, setup_database):
    # Имитация подключения к базе данных
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database
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


def test_check_coefficient_for_others():
    assert check_coefficient_for_others(5) == 6
    assert check_coefficient_for_others(0) == 1
    assert check_coefficient_for_others(21) == 20


@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_update_coefficient_for_users(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    Members.create(chat_id=331,
                   member_id=331,
                   coefficient=10,
                   pidor_coefficient=10,
                   full_name='test',
                   nick_name='test')

    assert update_coefficient_for_users(331, 2, 'nice') == None
    assert update_coefficient_for_users(331, 2, 'pidor') == None

@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_get_pidor_stats(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    Stats.create(chat_id=901, member_id=901, count=0)
    Stats.create(chat_id=902, member_id=902, count=0)

    assert get_pidor_stats(chat_id=901, stats_type='stats') == {901: 0}
    assert get_pidor_stats(chat_id=901, stats_type='pidor_stats') == 'Ни один пользователь не зарегистрирован, статистики нет'
    assert get_pidor_stats(chat_id=902, stats_type='stats') == {902: 0}


@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_get_user_percentage_nice_pidor(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    Stats.create(chat_id=911, member_id=911, count=0)
    PidorStats.create(chat_id=912, member_id=912, count=10)
    PidorStats.create(chat_id=913, member_id=913, count=50)
    PidorStats.create(chat_id=914, member_id=914, count=100)

    assert get_user_percentage_nice_pidor(911, 911) == {'member_id': 911, 'nice': 50, 'pidor': 50}
    assert get_user_percentage_nice_pidor(912, 912) == {'member_id': 912, 'nice': 0, 'pidor': 100}
    assert get_user_percentage_nice_pidor(913, 913) == {'member_id': 913, 'nice': 0, 'pidor': 100}
    assert get_user_percentage_nice_pidor(914, 914) == {'member_id': 914, 'nice': 0, 'pidor': 100}


@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_reset_stats_data(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database


    Stats.create(chat_id=921, member_id=921, count=5)
    PidorStats.create(chat_id=921, member_id=921, count=10)
    Members.create(chat_id=921, member_id=921, coefficient=10, pidor_coefficient=10, full_name='test',
                   nick_name='test')
    CurrentNice.create(chat_id=921, member_id=921, timestamp=0)

    assert reset_stats_data(921) == None

@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_update_current(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database
    CurrentNice.create(chat_id=931, member_id=931, timestamp=0)
    CurrentNice.create(chat_id=932, member_id=932, timestamp=0)

    assert update_current(931, 'current_nice', 931) == None
    assert update_current(932, 'current_pidor', 932) == None

@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_is_not_time_expired(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database
    CurrentNice.create(chat_id=941, member_id=941, timestamp=0)
    assert is_not_time_expired(941, 'current_nice') == False

@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_add_chat_to_carmic_dices_in_db(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    CarmicDicesEnabled.create(chat_id=952)

    assert add_chat_to_carmic_dices_in_db(951) == None
    assert add_chat_to_carmic_dices_in_db(952) == None

@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_remove_chat_from_carmic_dices_in_db(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    CarmicDicesEnabled.create(chat_id=961)

    assert remove_chat_from_carmic_dices_in_db(961) == None
    assert remove_chat_from_carmic_dices_in_db(962) == None

@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_get_current_user(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    CurrentNice.create(chat_id=971, member_id=971, timestamp=0)
    CurrentNice.create(chat_id=972, member_id=972, timestamp=0)

    assert get_current_user(971, 'current_nice') == {'id': 971, 'timestamp': 0}
    assert get_current_user(972, 'current_nice') == {'id': 972, 'timestamp': 0}


@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_set_full_name_and_nickname_in_db(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    Members.create(chat_id=981, member_id=981, coefficient=10, pidor_coefficient=10, full_name='test',
                   nick_name='test')

    assert set_full_name_and_nickname_in_db(981, 981, 'test1', 'test') == None


@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_get_full_name_from_db(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    Members.create(chat_id=991, member_id=991, coefficient=10, pidor_coefficient=10, full_name='test',
                   nick_name='test')

    assert get_full_name_from_db(991, 991) == 'test'

@mock.patch('nice_bot.run.dbhandle.connect')
@mock.patch('nice_bot.run.dbhandle.close')
def test_get_nickname_from_db(mock_connect, mock_close, setup_database):
    mock_connect.return_value = setup_database
    mock_close.return_value = setup_database

    Members.create(chat_id=1001, member_id=1001, coefficient=10, pidor_coefficient=10, full_name='test',
                   nick_name='test')

    assert get_nickname_from_db(1001, 1001) == 'test'




# Очистка данных после теста
# @pytest.fixture(autouse=True)
# def teardown_function():
#     yield
#     test_db.execute_sql('PRAGMA foreign_keys=OFF;')
#     test_db.drop_tables([PidorStickers])
#     test_db.execute_sql('PRAGMA foreign_keys=ON;')
#     test_db.close()



