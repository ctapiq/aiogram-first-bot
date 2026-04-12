from aiogram import Router, F, Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile, InputSticker
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from pdf2image import convert_from_path
from PIL import Image
import asyncio
import logging
import os
import aiohttp
from keyboards import get_cancel_keyboard, get_main_reply_keyboard

#12312
class Form(StatesGroup):
    fromuserphoto = State()
    firstsize = State()
    secondsize = State()
    resultphoto = State()
    pdf2photo = State()
    sticker = State()
    takephotosticker = State()
    whatidsticker = State()
    phototaked = State()
    resized_photo = State()
    tiktok_video = State()


logging.basicConfig(level=logging.INFO)






router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Откройте главное меню взаимодействия с ботом\nс помощью команды\n/menu")


@router.message(Command("menu"))
async def callmenu(message: Message):
    await message.answer(text="Главное меню открыто",reply_markup=(get_main_reply_keyboard()))

@router.message(Command("cancel"))
@router.message(F.text == "Отмена")
async def cancel (message: Message, state: FSMContext):
    data = await state.get_data()
    user_photo = data.get("fromuserphoto")
    if user_photo and os.path.exists(user_photo):
        try:
            os.remove(user_photo)
        except Exception as e:
            logging.error(f"Ошибка удаления: {e}")

    current_state = await state.get_state()
    logging.info(f"Действие отменено{message.from_user.id} в состоянии {current_state}")

    await state.clear()
    await message.answer("Действие отменено.", reply_markup=get_main_reply_keyboard())


@router.message(Command("TikTok"))
@router.message(F.text == "Скачать видео из тиктока без водяного знака")
async def start_tiktok(message: Message, state: FSMContext):
    await message.answer("Отправь мне ссылку на видео",
                         reply_markup=get_cancel_keyboard())
    await state.set_state(Form.tiktok_video)

@router.message(Form.tiktok_video, F.text.contains("tiktok.com"))
async def process_tiktok(message: Message, state: FSMContext):
    status_msg = await message.answer("Обработка..")

    url = message.text
    api_url = "https://www.tikwm.com/api/"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, params={"url": url, "hd": 1}) as response:
                res_data = await response.json()

                if res_data.get("code") == 0:
                    video_url = res_data["data"]["play"]
                    await message.answer_video(video_url, caption="Твое видео готово!")
                    await status_msg.delete()
                    await state.clear()
                else:
                    await status_msg.edit_text("Не удалось найти видео по ссылке")
        except Exception as e:
            logging.error(f"TikTok Error: {e}")
            await status_msg.edit_text("Произошла ошибка при загрузке")


@router.message(Command("whatidsticker"))
@router.message(F.text == "Узнать айди стикера")
async def takestick(message: Message, state: FSMContext):
    await message.answer("Отправь мне стикер айди которого тебя интересует")
    await state.set_state(Form.whatidsticker)


@router.message(Form.whatidsticker, F.sticker)
async def givestick(message: Message, state:FSMContext):    
    await message.answer_sticker(message.sticker.file_id)
    await message.answer(f"ID этого стикера:\n`{message.sticker.file_id}`", parse_mode="Markdown")
    await state.clear()

    


@router.message(Command("size"))
@router.message(F.text == "Изменить размер фото")
async def start_resize(message: Message, state: FSMContext):
    await message.answer("Я могу изменить размер твоего фото!\n Отправь мне фото которое нужно изменить!")
    await state.set_state(Form.fromuserphoto)


@router.message(Form.fromuserphoto, F.photo)
async def photo_processs(message: Message, state: FSMContext):
    await message.answer("А теперь введите ширину фото в пикселях", reply_markup=get_cancel_keyboard())
    photo = message.photo[-1]
    file_id = photo.file_id


    file_name = f"photos/{message.from_user.id}.jpg" 
    await message.bot.download(photo, destination=file_name)   
    await state.update_data(fromuserphoto=file_name)
    await state.set_state(Form.firstsize)


@router.message(Form.firstsize, F.text)
async def firstsize(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число в пикселях")
        return 
    width = int(message.text)
    if width > 5000 or width < 10:
        await message.answer("Размер должен быть от 10 до 5000 пикселей")
        return
    await message.answer("А теперь введите высоту фото в пикселях", reply_markup=get_cancel_keyboard())
    await state.update_data(width=message.text)
    await state.set_state(Form.secondsize)


@router.message(Form.secondsize, F.text)
async def secondtsize(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число в пикселях")
        return
    height = int(message.text)
    if height > 5000 or height < 10:
        await message.answer("Размер должен быть от 10 до 5000 пикселей")
        return
    await state.update_data(height=message.text)   
    data = await state.get_data()

    userphoto_original = data.get("fromuserphoto")
    width = int(data.get("width")) 
    height = int(data.get("height"))
    

    fromuserphoto = Image.open(userphoto_original)

    fromuserphoto = fromuserphoto.resize((width,height))
    photo_resized = f"photos/finallyphoto{message.from_user.id}.jpg"
    fromuserphoto.save(photo_resized)
    os.remove(userphoto_original)
    
    photo_to_send = FSInputFile(photo_resized)

    await message.answer_photo(photo_to_send, caption="Вот твое фото!",
                               reply_markup=get_main_reply_keyboard())
    os.remove(photo_resized)
    await state.clear()


@router.message(Command("pdf"))
@router.message(F.text == "PDF to JPG(webp)")
async def startpdf(message: Message, state: FSMContext):
    
    await message.answer("Пришлите мне свой PDF файл чтобы я его смог конвертировать в фото")
    await state.set_state(Form.pdf2photo)


@router.message(Form.pdf2photo, F.document)
async def getpdf(message: Message, state: FSMContext):
    if not message.document.file_name.lower().endswith(".pdf"):
        await message.answer_sticker("CAACAgIAAxkBAAOvadeOA_uOwAABqbM-yy4NQKkbPgtAAAITgQACuy3ASSzh33Kzo1pwOwQ")
        return
    pdffromuser = f"photos/{message.document.file_id}.pdf"
    await message.bot.download(message.document, destination=pdffromuser)
    

    pages = convert_from_path(pdffromuser, dpi=150)
    for i, page in enumerate(pages):
        result = f"photos/p_{i}_{message.from_user.id}.jpg"
        page.save(result, "JPEG")
        await message.answer_photo(FSInputFile(result))
        os.remove(result)

    os.remove(pdffromuser)

    await state.clear()


@router.message(Command("sticker"))
@router.message(F.text == "Получить стикер из фото")
async def take_photo(message: Message, state: FSMContext):
    await message.answer("Отправь мне фото который я должен добавить в стикерпак")
    await state.set_state(Form.sticker)


@router.message(Form.sticker, F.photo)
async def phototaked(message: Message, state: FSMContext):

    photo = message.photo[-1]
    file_id = photo.file_id
    await state.set_state(Form.phototaked)
   
    photo_path = f"photos/takedphotoforstick{message.from_user.id}.jpg"
    await message.bot.download(photo, destination=photo_path)
      
    img = Image.open(photo_path)

    new_img = img.resize((512, 512))
    resized_photo = f"photos/resizedphotostick{message.from_user.id}.webp"
    new_img.save(resized_photo) 
    img.close()
    os.remove(photo_path)

    user_id = message.from_user.id

    bot_obj = await message.bot.get_me()

    pack_name = f"user_{user_id}_stickers_by_{bot_obj.username}"
    pack_title = f"Pack by {message.from_user.first_name}"

    try:
        upload = await message.bot.upload_sticker_file(
            user_id=user_id,
            sticker=FSInputFile(resized_photo),
            sticker_format="static"
        )

        sticker_to_add = InputSticker(
            sticker=upload.file_id,
            emoji_list=["😊"],
            format="static"
        )
        try:
            await message.bot.add_sticker_to_set(
                user_id=user_id,
                name=pack_name,
                sticker=sticker_to_add
            )
            await message.answer(f"Стикер добавлен в твой набор!\nhttps://t.me/addstickers/{pack_name}")

        except Exception as e:
            if "STICKERSET_INVALID" in str(e):
                await message.bot.create_new_sticker_set(
                    user_id=user_id,
                    name=pack_name,
                    title=pack_title,
                    stickers=[sticker_to_add],
                    sticker_format="static"
                ) 
                await message.answer(f"🎉 Создан твой первый стикерпак!\nhttps://t.me/addstickers/{pack_name}")
            else:
                await message.answer(f"Произошла ошибка: {e}")
    finally: 
            
        if os.path.exists(resized_photo):
            os.remove(resized_photo)
        await state.clear()
