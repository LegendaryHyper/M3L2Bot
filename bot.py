import discord
from discord.ext import commands
from logic import DB_Manager
from discord import ui, ButtonStyle
from config import DATABASE, TOKEN  

intents = discord.Intents.default() 
intents.messages = True
intents.message_content = True # Intentler

class TestModal(ui.Modal, title='Test başlık'):
    # Modal pencerede metin alanları tanımlama
    field_1 = ui.TextInput(label='Kısa metin')
    field_2 = ui.TextInput(label='Uzun metin', style=discord.TextStyle.paragraph)

    # Modal pencere istendiğinde çağrılan bir yöntem
    async def on_submit(self, interaction: discord.Interaction):
        # Girilen verilerle mesajı güncelleme
        await interaction.message.edit(content=f'Kısa metin: {self.field_1.value}\n'
                                               f'Uzun metin: {self.field_2.value}')
        # Yanıtın daha önce gönderilip gönderilmediğini kontrol etme
        if not interaction.response.is_done():
            # Gecikmeli yanıt için hazırlık yapma
            await interaction.response.defer()
class ProjectModal(ui.Modal, title='Proje Ekleme'):
    # Modal pencerede metin alanları tanımlama
    project_name = ui.TextInput(label='Proje Adı')
    project_link = ui.TextInput(label='Projeye Dair Bağlantı')
    project_cur_status = ui.TextInput(label='Projenin Anlık Durumu')
    project_description = ui.TextInput(label='Açıklama', required=False, style=discord.TextStyle.paragraph)
    
    def __init__(self, *, title = "Proje Ekleme", timeout = None, custom_id = "project_modal", user_id = None):
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        self.user_id = user_id
    
    # Modal pencere istendiğinde çağrılan bir yöntem
    async def on_submit(self, interaction: discord.Interaction):
        # Girilen verilerle mesajı güncelleme
        status_id = manager.get_status_id(self.project_cur_status.value)
        
        #await interaction.message.edit(content=f'Kısa metin: {self.field_1.value}\n'
        #                                       f'Uzun metin: {self.field_2.value}')
        # Yanıtın daha önce gönderilip gönderilmediğini kontrol etme
        if self.project_description.value != "": # Açıklamada yazı olup olmadığının kontrolü. Yazı varsa açıklama dahil veri tabanına eklenir.
            data = [self.user_id, self.project_name.value, self.project_description.value, self.project_link.value, status_id]
            manager.insert_project_w_desc([tuple(data)])
        else: # Açıklama boşsa açıklama olmaksızın eklenir.
            data = [self.user_id, self.project_name.value, "No description", self.project_link.value, status_id]
            manager.insert_project_w_desc([tuple(data)])
        
        if not interaction.response.is_done():
            # Gecikmeli yanıt için hazırlık yapma
            await interaction.response.defer()
# Buton tanımlama
class TestButton(ui.Button):
    # Belirli özellikler sahip bir butonun başlatılması
    def __init__(self, label="Proje ekle", style=ButtonStyle.blurple, row=0, user_id = None):
        super().__init__(label=label, style=style, row=row)
        self.user_id = user_id

    # Butona basıldığında çağrılan bir yöntem
    async def callback(self, interaction: discord.Interaction):
        # Kullanıcıya doğrudan mesaj gönderme
        #await interaction.user.send("Bir butona bastınız")
        # Butona basılan kanala bir mesaj gönderme
        #await interaction.message.channel.send("Bir butona bastınız")
        # Modal pencereyi açma
        await interaction.response.send_modal(ProjectModal(user_id=self.user_id))
        # Basıldıktan sonra butonun stilini değiştirme
        self.style = ButtonStyle.gray

        # Yanıtın daha önce gönderilip gönderilmediğini kontrol etme
        if not interaction.response.is_done():
            # Gecikmeli yanıt için hazırlık yapma
            await interaction.response.defer()

# Buton içeren bir pencere (görünüm) nesnesi tanımlama
class TestView(ui.View):
    # Görünümü başlatma
    def __init__(self, user_id = None):
        super().__init__()
        # Görünüme bir buton ekleme
        self.user_id = user_id
        self.add_item(TestButton(label="Proje ekle", user_id=self.user_id))

bot = commands.Bot(command_prefix='!', intents=intents)
manager = DB_Manager(DATABASE)

@bot.event
async def on_ready(): # Bot hazır olduğunda terminalde bildirir.
    print(f'Bot hazır! {bot.user} olarak giriş yapıldı.')

# Butonu gösteren bir komut
@bot.command()
async def test(ctx):
    # Bir buton içeren görünüm ile mesaj gönderme
    await ctx.send("Aşağıdaki butona tıklayın:", view=TestView(user_id=ctx.author.id))

@bot.command(name='start') # (!start) komutu ile botun kendini tanıtması sağlanır.
async def start_command(ctx):
    await ctx.send("Merhaba! Ben bir proje yöneticisi botuyum.\nProjelerinizi ve onlara dair tüm bilgileri saklamanıza yardımcı olacağım! =)")
    await info(ctx)

@bot.command(name='info')
async def info(ctx): # (!info) komutu ile diğer komutlara dair bilgi verdirtir.
    await ctx.send("""
Kullanabileceğiniz komutlar şunlardır:

!new_project - yeni bir proje eklemek
!projects - tüm projelerinizi listelemek
!update_projects - proje verilerini güncellemek
!skills - belirli bir projeye beceri eklemek
!delete - bir projeyi silmek

Ayrıca, proje adını yazarak projeyle ilgili tüm bilgilere göz atabilirsiniz!""")

@bot.command(name='new_project')
async def new_project(ctx): # (!new_project) komutu ile yönergeler verilir ve yeni proje girilmesi sağlanır.
    await ctx.send("Lütfen projenin adını girin!")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    name = await bot.wait_for('message', check=check)
    data = [ctx.author.id, name.content]
    await ctx.send("Lütfen projeye ait bağlantıyı gönderin!")
    link = await bot.wait_for('message', check=check)
    data.append(link.content)

    statuses = [x[0] for x in manager.get_statuses()]
    await ctx.send("Lütfen projenin mevcut durumunu girin!", delete_after=60.0)
    await ctx.send("\n".join(statuses), delete_after=60.0)
    
    status = await bot.wait_for('message', check=check)
    if status.content not in statuses:
        await ctx.send("Seçtiğiniz durum listede bulunmuyor. Lütfen tekrar deneyin!", delete_after=60.0)
        return

    status_id = manager.get_status_id(status.content)
    data.append(status_id)
    manager.insert_project([tuple(data)])
    await ctx.send("Proje kaydedildi")

@bot.command(name='projects')
async def get_projects(ctx): # (!projects) komutu ile projeleri döndürür.
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)
    if projects:
        text = "\n".join([f"Project name: {x[2]} \nLink: {x[4]}\n" for x in projects])
        await ctx.send(text)
    else:
        await ctx.send('Henüz herhangi bir projeniz yok!\nBir tane eklemeyi düşünün! !new_project komutunu kullanabilirsiniz.')

@bot.command(name='skills') # (!skills) komutu ile bir projeye beceri ekleyebilirsiniz.
async def skills(ctx):
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        await ctx.send('Bir beceri eklemek istediğiniz projeyi seçin')
        await ctx.send("\n".join(projects))

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        project_name = await bot.wait_for('message', check=check)
        if project_name.content not in projects:
            await ctx.send('Bu projeye sahip değilsiniz, lütfen tekrar deneyin! Beceri eklemek istediğiniz projeyi seçin')
            return

        skills = [x[1] for x in manager.get_skills()]
        await ctx.send('Bir beceri seçin')
        await ctx.send("\n".join(skills))

        skill = await bot.wait_for('message', check=check)
        if skill.content not in skills:
            await ctx.send('Görünüşe göre seçtiğiniz beceri listede yok! Lütfen tekrar deneyin! Bir beceri seçin')
            return

        manager.insert_skill(user_id, project_name.content, skill.content)
        await ctx.send(f'{skill.content} becerisi {project_name.content} projesine eklendi')
    else:
        await ctx.send('Henüz herhangi bir projeniz yok!\nBir tane eklemeyi düşünün! !new_project komutunu kullanabilirsiniz.')

@bot.command(name='delete') # (!delete) komutu ile proje silinir.
async def delete_project(ctx):
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        await ctx.send("Silmek istediğiniz projeyi seçin")
        await ctx.send("\n".join(projects))

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        project_name = await bot.wait_for('message', check=check)
        if project_name.content not in projects:
            await ctx.send('Bu projeye sahip değilsiniz, lütfen tekrar deneyin!')
            return

        project_id = manager.get_project_id(project_name.content, user_id)
        manager.delete_project(user_id, project_id)
        await ctx.send(f'{project_name.content} projesi veri tabanından silindi!')
    else:
        await ctx.send('Henüz herhangi bir projeniz yok!\nBir tane eklemeyi düşünün! !new_project komutunu kullanabilirsiniz.')

@bot.command(name='update_projects') # (!update_projects) komutu ile proje güncellenir.
async def update_projects(ctx):
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        await ctx.send("Güncellemek istediğiniz projeyi seçin")
        await ctx.send("\n".join(projects))

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        project_name = await bot.wait_for('message', check=check)
        if project_name.content not in projects:
            await ctx.send("Bir hata oldu! Lütfen güncellemek istediğiniz projeyi tekrar seçin:")
            return

        await ctx.send("Projede neyi değiştirmek istersiniz?")
        attributes = {'Proje adı': 'project_name', 'Açıklama': 'description', 'Proje bağlantısı': 'url', 'Proje durumu': 'status_id'}
        await ctx.send("\n".join(attributes.keys()))

        attribute = await bot.wait_for('message', check=check)
        if attribute.content not in attributes:
            await ctx.send("Hata oluştu! Lütfen tekrar deneyin!")
            return

        if attribute.content == 'Durum':
            statuses = manager.get_statuses()
            await ctx.send("Projeniz için yeni bir durum seçin")
            await ctx.send("\n".join([x[0] for x in statuses]))
            update_info = await bot.wait_for('message', check=check)
            if update_info.content not in [x[0] for x in statuses]:
                await ctx.send("Yanlış durum seçildi, lütfen tekrar deneyin!")
                return
            update_info = manager.get_status_id(update_info.content)
        else:
            await ctx.send(f"{attribute.content} için yeni bir değer girin")
            update_info = await bot.wait_for('message', check=check)
            update_info = update_info.content

        manager.update_projects(attributes[attribute.content], (update_info, project_name.content, user_id))
        await ctx.send("Tüm işlemler tamamlandı! Proje güncellendi!")
    else:
        await ctx.send('Henüz herhangi bir projeniz yok!\nBir tane eklemeyi düşünün! !new_project komutunu kullanabilirsiniz.')

bot.run(TOKEN) # Bot TOKEN kullanılarak kaldırılır.