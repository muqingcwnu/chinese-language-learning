from django.core.management.base import BaseCommand
from mandarin_vocab.models import HSKBook, BookChapter

class Command(BaseCommand):
    help = 'Create HSK books and their chapters'

    def handle(self, *args, **options):
        # Create HSK1 Book
        hsk1_book, _ = HSKBook.objects.get_or_create(
            title='HSK1 Standard Course Textbook',
            hsk_level=1,
            book_type='TB',
            defaults={
                'description': 'Official HSK1 Standard Course Textbook',
                'page_count': 200
            }
        )

        # Define chapters with Chinese, Pinyin, and English titles
        chapters = [
            {
                "title": "你好 (Nǐ hǎo) - Hello",
                "chinese_title": "你好",
                "pinyin_title": "Nǐ hǎo",
                "english_title": "Hello",
                "description": "Basic greetings and introductions",
                "chinese_text": "李明：你好！\n王红：你好！\n李明：你是王红吗？\n王红：是，我是王红。你是李明吗？\n李明：是，我是李明。很高兴认识你！\n王红：我也很高兴认识你！",
                "pinyin_text": "Lǐ Míng: Nǐ hǎo!\nWáng Hóng: Nǐ hǎo!\nLǐ Míng: Nǐ shì Wáng Hóng ma?\nWáng Hóng: Shì, wǒ shì Wáng Hóng. Nǐ shì Lǐ Míng ma?\nLǐ Míng: Shì, wǒ shì Lǐ Míng. Hěn gāoxìng rènshi nǐ!\nWáng Hóng: Wǒ yě hěn gāoxìng rènshi nǐ!"
            },
            {
                "title": "数字 (Shùzì) - Numbers",
                "chinese_title": "数字",
                "pinyin_title": "Shùzì",
                "english_title": "Numbers",
                "description": "Numbers and basic counting in Mandarin",
                "chinese_text": "老师：你多大了？\n学生：我二十岁了。\n老师：他呢？\n学生：他十八岁。\n老师：她比他大吗？\n学生：是的，她二十二岁。",
                "pinyin_text": "Lǎoshī: Nǐ duō dà le?\nXuésheng: Wǒ èrshí suì le.\nLǎoshī: Tā ne?\nXuésheng: Tā shíbā suì.\nLǎoshī: Tā bǐ tā dà ma?\nXuésheng: Shì de, tā èrshí'èr suì."
            },
            {
                "title": "家人 (Jiārén) - Family",
                "chinese_title": "家人",
                "pinyin_title": "Jiārén",
                "english_title": "Family",
                "description": "Family members and relationships",
                "chinese_text": "小明：这是我的家。\n妈妈：你好！我是小明的妈妈。\n爸爸：我是他的爸爸。\n小明：这是我的姐姐。\n姐姐：大家好！",
                "pinyin_text": "Xiǎo Míng: Zhè shì wǒ de jiā.\nMāma: Nǐ hǎo! Wǒ shì Xiǎo Míng de māma.\nBàba: Wǒ shì tā de bàba.\nXiǎo Míng: Zhè shì wǒ de jiějie.\nJiějie: Dàjiā hǎo!"
            },
            {
                "title": "时间 (Shíjiān) - Time",
                "chinese_title": "时间",
                "pinyin_title": "Shíjiān",
                "english_title": "Time",
                "description": "Telling time and daily schedule",
                "chinese_text": "老师：现在几点？\n学生：现在八点半。\n老师：你什么时候去学校？\n学生：我七点去学校。",
                "pinyin_text": "Lǎoshī: Xiànzài jǐ diǎn?\nXuésheng: Xiànzài bā diǎn bàn.\nLǎoshī: Nǐ shénme shíhou qù xuéxiào?\nXuésheng: Wǒ qī diǎn qù xuéxiào."
            },
            {
                "title": "饮食 (Yǐnshí) - Food",
                "chinese_title": "饮食",
                "pinyin_title": "Yǐnshí",
                "english_title": "Food",
                "description": "Food, drinks, and ordering",
                "chinese_text": "服务员：你想喝什么？\n小明：我要一杯茶。\n服务员：你想吃什么？\n小明：我要一碗米饭。",
                "pinyin_text": "Fúwùyuán: Nǐ xiǎng hē shénme?\nXiǎo Míng: Wǒ yào yī bēi chá.\nFúwùyuán: Nǐ xiǎng chī shénme?\nXiǎo Míng: Wǒ yào yī wǎn mǐfàn."
            },
            {
                "title": "日常生活 (Rìcháng Shēnghuó) - Daily Life",
                "chinese_title": "日常生活",
                "pinyin_title": "Rìcháng Shēnghuó",
                "english_title": "Daily Life",
                "description": "Daily activities and routines",
                "chinese_text": "小李：你每天几点起床？\n小王：我每天六点起床。\n小李：你几点去上班？\n小王：我七点半去上班。",
                "pinyin_text": "Xiǎo Lǐ: Nǐ měitiān jǐ diǎn qǐchuáng?\nXiǎo Wáng: Wǒ měitiān liù diǎn qǐchuáng.\nXiǎo Lǐ: Nǐ jǐ diǎn qù shàngbān?\nXiǎo Wáng: Wǒ qī diǎn bàn qù shàngbān."
            },
            {
                "title": "地点方向 (Dìdiǎn Fāngxiàng) - Places",
                "chinese_title": "地点方向",
                "pinyin_title": "Dìdiǎn Fāngxiàng",
                "english_title": "Places and Directions",
                "description": "Locations and directions",
                "chinese_text": "游客：请问，图书馆在哪里？\n学生：图书馆在学校的右边。\n游客：远吗？\n学生：不远，走路五分钟。",
                "pinyin_text": "Yóukè: Qǐngwèn, túshūguǎn zài nǎli?\nXuésheng: Túshūguǎn zài xuéxiào de yòubian.\nYóukè: Yuǎn ma?\nXuésheng: Bù yuǎn, zǒulù wǔ fēnzhōng."
            },
            {
                "title": "购物 (Gòuwù) - Shopping",
                "chinese_title": "购物",
                "pinyin_title": "Gòuwù",
                "english_title": "Shopping",
                "description": "Shopping and prices",
                "chinese_text": "顾客：这件衣服多少钱？\n店员：八十九块钱。\n顾客：太贵了！\n店员：七十块，便宜点。",
                "pinyin_text": "Gùkè: Zhè jiàn yīfu duōshao qián?\nDiànyuán: Bāshíjiǔ kuài qián.\nGùkè: Tài guì le!\nDiànyuán: Qīshí kuài, piányi diǎn."
            },
            {
                "title": "天气 (Tiānqì) - Weather",
                "chinese_title": "天气",
                "pinyin_title": "Tiānqì",
                "english_title": "Weather",
                "description": "Weather and seasons",
                "chinese_text": "小明：今天天气怎么样？\n小红：今天天气很好，不冷不热。\n小明：明天呢？\n小红：明天可能会下雨。",
                "pinyin_text": "Xiǎo Míng: Jīntiān tiānqì zěnmeyàng?\nXiǎo Hóng: Jīntiān tiānqì hěn hǎo, bù lěng bù rè.\nXiǎo Míng: Míngtiān ne?\nXiǎo Hóng: Míngtiān kěnéng huì xià yǔ."
            },
            {
                "title": "基本会话 (Jīběn Huìhuà) - Basic Conversations",
                "chinese_title": "基本会话",
                "pinyin_title": "Jīběn Huìhuà",
                "english_title": "Basic Conversations",
                "description": "Common conversational phrases",
                "chinese_text": "A：你好！最近怎么样？\nB：我很好，谢谢。你呢？\nA：我也不错。你周末做什么？\nB：我要去看电影。",
                "pinyin_text": "A: Nǐ hǎo! Zuìjìn zěnmeyàng?\nB: Wǒ hěn hǎo, xièxie. Nǐ ne?\nA: Wǒ yě bùcuò. Nǐ zhōumò zuò shénme?\nB: Wǒ yào qù kàn diànyǐng."
            }
        ]

        # Create chapters
        for index, chapter_data in enumerate(chapters, 1):
            chapter, created = BookChapter.objects.update_or_create(
                book=hsk1_book,
                chapter_number=index,
                defaults={
                    'title': chapter_data['title'],
                    'description': chapter_data['description'],
                    'chinese_text': chapter_data['chinese_text'],
                    'pinyin_text': chapter_data['pinyin_text'],
                    'start_page': (index - 1) * 20 + 1,
                    'end_page': index * 20
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created chapter {index}: {chapter.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated chapter {index}: {chapter.title}'))

        self.stdout.write(self.style.SUCCESS('Successfully created HSK books and chapters with content')) 