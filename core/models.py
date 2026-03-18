from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField

# --- 0. NOTÍCIAS (RESTAURADO) ---
class Noticia(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título da Notícia")
    subtitulo = models.CharField(max_length=300, blank=True, verbose_name="Resumo / Subtítulo")
    conteudo = RichTextField(verbose_name="Conteúdo Completo")
    autor = models.CharField(max_length=100, default="Assessoria FEPI")

    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Slug (URL Amigável)")
    imagem_capa = models.ImageField(upload_to='noticias/', blank=True, null=True, verbose_name="Imagem de Capa")
    data_publicacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Publicação")

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ['-data_publicacao']

    def __str__(self):
        return self.titulo


# 1. Informações de Contato
class InformacaoContato(models.Model):
    endereco = models.CharField(max_length=300, default="R. Olavo Bilac, 1394 - Centro (Sul)")
    cidade = models.CharField(max_length=100, default="Teresina - PI")
    cep = models.CharField(max_length=20, default="64001-280")
    telefone = models.CharField(max_length=50, default="(86) 3221-3021")
    email = models.EmailField(blank=True)
    horario_livraria = models.CharField(max_length=200, default="Segunda à Sábado")

    def save(self, *args, **kwargs):
        if not self.pk and InformacaoContato.objects.exists():
            return
        super(InformacaoContato, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Configuração de Contato"
        verbose_name_plural = "Configuração de Contato"

    def __str__(self):
        return "Dados de Contato da FEPI"

# --- ESTRUTURA ORGANIZACIONAL ---

class TipoDiretoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Tipo de Diretoria/Departamento")
    descricao = models.CharField(max_length=255, blank=True, verbose_name="Descrição Breve")
    ordem = models.IntegerField(default=1, verbose_name="Ordem de Exibição")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo/Departamento"
        verbose_name_plural = "Tipos e Departamentos"
        ordering = ['ordem']

class Cargo(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Cargo")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Cargo Presidência e Departamentos"
        verbose_name_plural = "Cargos Presidência e Departamentos"
        ordering = ['nome']


# 2. Página Institucional
class PaginaInstitucional(models.Model):
    titulo = models.CharField(max_length=200, default="Nossa História")
    conteudo = RichTextField(verbose_name="Texto da História")
    frase_destaque = models.CharField(max_length=300, verbose_name="Frase de Destaque (Missão)", blank=True)

    ano_inicio = models.IntegerField(default=2024, verbose_name="Ano Início da Gestão")
    ano_fim = models.IntegerField(default=2027, verbose_name="Ano Fim da Gestão")

    def save(self, *args, **kwargs):
        if not self.pk and PaginaInstitucional.objects.exists(): return
        super(PaginaInstitucional, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Página Institucional (Texto)"
        verbose_name_plural = "Página Institucional (Texto)"

    def __str__(self):
        return f"Configuração da Página Principal ({self.ano_inicio}-{self.ano_fim})"


class MembroDiretoria(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Responsável")
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, verbose_name="Cargo")
    tipo = models.ForeignKey(TipoDiretoria, on_delete=models.PROTECT, verbose_name="Tipo/Departamento")

    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, verbose_name="Email")
    ordem = models.IntegerField(default=0, help_text="Para ordenar dentro do Tipo/Departamento")

    class Meta:
        verbose_name = "Membro/Responsável"
        verbose_name_plural = "Membros e Responsáveis"
        ordering = ['tipo__ordem', 'ordem', 'nome']

    def __str__(self):
        return f"{self.cargo.nome} ({self.nome})"


# 4. Configuração da Home (Banner e Pop-up)
class ConfiguracaoHome(models.Model):
    # --- BANNER PRINCIPAL ---
    titulo_banner = models.CharField(max_length=200, default="Federação Espírita do Piauí")
    subtitulo_banner = models.CharField(max_length=300, default="Unindo corações, esclarecendo mentes e consolando almas.")
    imagem_banner = models.ImageField(upload_to='banners/', blank=True, null=True, help_text="Imagem de fundo do topo (Opcional)")

    # --- POP-UP MODAL (MARKETING) ---
    popup_ativo = models.BooleanField(default=False, verbose_name="Ativar Pop-up?")
    popup_titulo = models.CharField(max_length=100, blank=True, verbose_name="Título do Pop-up")
    popup_imagem = models.ImageField(upload_to='popup/', blank=True, null=True, verbose_name="Imagem do Pop-up")
    popup_link = models.URLField(blank=True, verbose_name="Link de Destino (Notícia/Curso)")
    popup_botao_texto = models.CharField(max_length=50, default="Saiba Mais", verbose_name="Texto do Botão")

    popup_inicio = models.DateTimeField(default=timezone.now, verbose_name="Início da Exibição")
    popup_fim = models.DateTimeField(default=timezone.now, verbose_name="Fim da Exibição")

    def save(self, *args, **kwargs):
        if not self.pk and ConfiguracaoHome.objects.exists():
            return
        super(ConfiguracaoHome, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Configuração da Home (Banner/Pop-up)"
        verbose_name_plural = "Configuração da Home (Banner/Pop-up)"

    def __str__(self):
        return "Configuração da Página Inicial"

# 4.1 Configuração do YouTube
class ConfiguracaoYouTube(models.Model):
    YT_MODE_CHOICES = (
        ('auto', 'Automático (último do canal)'),
        ('fixed', 'Fixo (ID informado)'),
        ('off', 'Desligado'),
    )

    youtube_mode = models.CharField(
        max_length=10,
        choices=YT_MODE_CHOICES,
        default='auto',
        verbose_name="Modo do YouTube"
    )

    youtube_channel_id = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        verbose_name="Channel ID",
        help_text="Ex: UCxxxx... (ID do canal)"
    )

    youtube_video_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Video ID (modo fixo)",
        help_text="Somente o ID do vídeo (ex: ABC1234)"
    )

    def save(self, *args, **kwargs):
        if not self.pk and ConfiguracaoYouTube.objects.exists():
            return
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Configuração do YouTube"
        verbose_name_plural = "Configuração do YouTube"

    def __str__(self):
        return "Configuração do YouTube"


# 5. Posts do Instagram
class PostInstagram(models.Model):
    imagem = models.ImageField(upload_to='instagram/', verbose_name="Imagem do Post")
    link = models.URLField(verbose_name="Link do Post (Instagram)")
    legenda = models.CharField(max_length=100, blank=True, help_text="Texto curto para acessibilidade")
    data_post = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Post do Instagram"
        verbose_name_plural = "Posts do Instagram (Vitrine)"
        ordering = ['-data_post']

    def __str__(self):
        return self.legenda or "Post Instagram"

# --- MÓDULO DE SECRETARIA / PROGRAMAÇÃO (Adicionado ao Core) ---

# 1. Atividades Semanais (Fixas)
class AtividadeSemanal(models.Model):
    DIAS_SEMANA = (
        ('SEG', 'Segunda-feira'),
        ('TER', 'Terça-feira'),
        ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'),
        ('SEX', 'Sexta-feira'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    )

    dia = models.CharField(max_length=3, choices=DIAS_SEMANA, verbose_name="Dia da Semana")
    horario = models.TimeField(verbose_name="Horário")
    nome = models.CharField(max_length=200, verbose_name="Nome da Atividade")
    descricao = models.CharField(max_length=300, blank=True, verbose_name="Descrição Curta")
    publico_alvo = models.CharField(max_length=100, default="Público Geral")

    class Meta:
        verbose_name = "Atividade Semanal"
        verbose_name_plural = "Atividades Semanais (Grade Fixa)"
        ordering = ['dia', 'horario']

    def __str__(self):
        return f"{self.get_dia_display()} - {self.nome}"


# 2. Palestras Públicas (Agenda de Oradores)
class PalestraPublica(models.Model):
    data_hora = models.DateTimeField(verbose_name="Data e Horário")
    tema = models.CharField(max_length=200, verbose_name="Tema da Palestra")
    orador = models.CharField(max_length=150, verbose_name="Orador / Expositor")
    casa_espirita = models.CharField(max_length=150, blank=True, verbose_name="Casa Espírita (Origem)", help_text="Deixar em branco se for da casa")

    imagem_divulgacao = models.ImageField(upload_to='palestras/', blank=True, null=True, verbose_name="Cartaz de Divulgação")
    link_transmissao = models.URLField(blank=True, null=True, verbose_name="Link YouTube (se houver)")

    class Meta:
        verbose_name = "Palestra Pública"
        verbose_name_plural = "Agenda de Palestras"
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.data_hora.strftime('%d/%m')} - {self.tema}"


# 3. Cursos e Eventos Especiais
class EventoAgenda(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título do Evento")

    # Campo Slug Adicionado para SEO e Sitemaps
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="Slug (URL)")

    data_inicio = models.DateTimeField(verbose_name="Início")
    data_fim = models.DateTimeField(verbose_name="Fim", blank=True, null=True)
    local = models.CharField(max_length=200, default="Auditório da FEPI")

    descricao = RichTextField(verbose_name="Detalhes do Evento")
    imagem = models.ImageField(upload_to='eventos/', blank=True, null=True, verbose_name="Banner/Cartaz")

    link_inscricao = models.URLField(blank=True, null=True, verbose_name="Link de Inscrição")
    valor = models.CharField(max_length=50, blank=True, verbose_name="Valor (se houver)", help_text="Ex: Gratuito ou R$ 20,00")

    destaque_home = models.BooleanField(default=False, verbose_name="Destacar na Home?")

    class Meta:
        verbose_name = "Evento / Curso"
        verbose_name_plural = "Agenda de Eventos e Cursos"
        ordering = ['data_inicio']

    def __str__(self):
        return self.titulo