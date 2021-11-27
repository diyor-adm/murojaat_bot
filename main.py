from telegram.ext import Updater, MessageHandler, ConversationHandler, CommandHandler, CallbackContext, Filters
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, MessageEntity
from datetime import datetime
import django
import os
import sys


sys.dont_write_bytecode = True
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from db.models import Appeal

updater: Updater = Updater(
    token='2073307763:AAHhuynOe4Lex93k0BWDvUqoGH5gvjKm42o')
dispatcher = updater.dispatcher
MENU_STATE, FIRST_NAME_STATE, LAST_NAME_STATE, REGION_STATE, ADDRESS_STATE, PHONE_STATE, APPEAL_STATE = range(
    7)


def menu_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton('Yangi murojaat')],
        [KeyboardButton('Mening murojaatlarim')]
    ], resize_keyboard=True, one_time_keyboard=True)


def phone_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton('Telefon raqam yuborish', request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)


def region_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton('Nurafshon shahri')],
        [KeyboardButton('O`rta Chirchiq tumani')]
    ], resize_keyboard=True, one_time_keyboard=True)


def start_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Salom', reply_markup=menu_keyboard())
    return MENU_STATE


def menu_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Sizga kerakli bo`limni tanlang', reply_markup=menu_keyboard())
    return MENU_STATE


def new_appeal_handler(update: Update, context: CallbackContext):

    update.message.reply_text('Ismingizni kiriting')
    return FIRST_NAME_STATE


def first_name_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'first_name': update.message.text,
    })
    print(context.chat_data)
    update.message.reply_text('Ajoyib! Ana endi familiyangizni kiriting!')
    return LAST_NAME_STATE


def last_name_resend_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Familiyangizni kiriting!')


def region_resend_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Iltimos quyidan yashash tuman yoki shahringizni tanlang!')


def address_resend_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Iltimos yashash joyingizni to`liq kiriting!')


def last_name_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'last_name': update.message.text,
    })
    print(context.chat_data)
    update.message.reply_text(
        'Ajoyib! Quyida istiqomat qiluvchi tuman yoki shahringizni tanlang!', reply_markup=region_keyboard())
    return REGION_STATE


def region_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'region': update.message.text,
    })
    print(context.chat_data)
    update.message.reply_text(
        'Ajoyib! Ana endi Yashash joyingizni to`liq kiriting')
    return ADDRESS_STATE


def address_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'address': update.message.text,
    })
    print(context.chat_data)
    update.message.reply_text(
        'Telefon raqamingizni kiriting yoki pastdagi tugmani bosing', reply_markup=phone_keyboard())

    return PHONE_STATE


def phone_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'phone_number': update.message.text,
    })
    print(context.chat_data)
    update.message.reply_text(
        'Murajaat qilishingiz sababini to`liq yozing', reply_markup=ReplyKeyboardRemove())
    return APPEAL_STATE


def phone_entity_handler(update: Update, context: CallbackContext):
    phone_number_entity = pne = list(
        filter(lambda e: e.type == 'phone_number', update.message.entities))[0]
    print(phone_number_entity)
    phone_number = update.message.text[pne.offset:pne.offset + pne.length]
    context.chat_data.update({
        'phone_number': phone_number,
    })
    print(context.chat_data)
    update.message.reply_text(
        'Murajaat qilishingiz sababini to`liq yozing', reply_markup=ReplyKeyboardRemove())
    return APPEAL_STATE


def phone_contact_handler(update: Update, context: CallbackContext):
    phone_number = update.message.contact['phone_number']
    context.chat_data.update({
        'phone_number': f'+{phone_number}',
    })
    print(context.chat_data)
    update.message.reply_text(
        'Murojaat qilishingiz sababini to`liq yozing', reply_markup=ReplyKeyboardRemove())
    return APPEAL_STATE


def phone_resend_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Iltimos telefon raqamingizni +998901234657 ko`rinishida kiriting yoki pastdagi tugmani bosing',
                              reply_markup=phone_keyboard())


def appeal_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'appeal': update.message.text,
    })
    print(context.chat_data)

    cd = context.chat_data

    appeal = Appeal.objects.create(
        first_name=cd['first_name'][0:255],
        last_name=cd['last_name'][0:255],
        region=cd['region'][0:255],
        address=cd['address'][0:255],
        phone_number=cd['phone_number'][0:63],
        appeal=cd['appeal'],
        user_id=update.effective_user.id
    )
    print(appeal)

    update.message.reply_text(
        'Murojaatingiz qabul qilindi. Tez orada aloqaga chiqamiz')
    return menu_handler(update, context)


def appeal_resend_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Iltimos murojaatingizni matn ko`rinishida qoldiring!')


def all_appeal_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Mening oxirgi 5 ta murojaatim')
    appeals = Appeal.objects.order_by('-id').filter(user_id=update.effective_user.id)[:5]
    print(appeals)
    if len(appeals) == 0:
        update.message.reply_text('Siz hech qanday murojaat qoldirmagansiz!')
    else:
        for appeal in appeals:
            update.message.reply_text(f'{appeal.appeal}'\
                f'\n\n'\
                f'_{appeal.first_name}_ _{appeal.last_name}_'\
                , parse_mode='Markdown')


def stop_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Hayr!', reply_markup=ReplyKeyboardRemove())


dispatcher.add_handler(ConversationHandler(
    entry_points=[
        MessageHandler(Filters.all, start_handler)],
    states={
        MENU_STATE: [
            MessageHandler(Filters.regex(r'^Yangi murojaat$'),
                           new_appeal_handler),
            MessageHandler(Filters.regex(
                r'^Mening murojaatlarim$'), all_appeal_handler),
            MessageHandler(Filters.all, menu_handler)
        ],
        FIRST_NAME_STATE: [
            MessageHandler(Filters.text, first_name_handler),
            MessageHandler(Filters.all, new_appeal_handler),
        ],
        LAST_NAME_STATE: [
            MessageHandler(Filters.text, last_name_handler),
            MessageHandler(Filters.all, last_name_resend_handler),
        ],
        REGION_STATE: [
            MessageHandler(Filters.regex(
                r'^Nurafshon shahri$'), region_handler),
            MessageHandler(Filters.regex(
                r'^O`rta Chirchiq tumani$'), region_handler),
            MessageHandler(Filters.all, region_resend_handler),
        ],
        ADDRESS_STATE: [
            MessageHandler(Filters.text, address_handler),
            MessageHandler(Filters.all, address_resend_handler),
        ],
        PHONE_STATE: [
            MessageHandler(Filters.text & Filters.entity(
                MessageEntity.PHONE_NUMBER), phone_entity_handler),
            MessageHandler(Filters.contact, phone_contact_handler),
            MessageHandler(Filters.all, phone_resend_handler),
        ],
        ADDRESS_STATE: [
            MessageHandler(Filters.text, address_handler),
            MessageHandler(Filters.all, address_resend_handler),
        ],
        APPEAL_STATE: [
            MessageHandler(Filters.text, appeal_handler),
            MessageHandler(Filters.all, appeal_resend_handler),
        ],
    },


    fallbacks=['stop', stop_handler],

))

updater.start_polling()
updater.idle()
