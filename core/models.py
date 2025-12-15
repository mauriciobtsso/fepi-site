from django.db import models
from django.utils import timezone # Importação para data/hora
from ckeditor.fields import RichTextField # Importação para o Editor de Texto

# 1. Informações de Contato (Rodapé e Fale Conosco)
class InformacaoContato(models.Model):
    endereco = models.CharField(max_length=300, default="R. Olavo Bilac, 1394 - Centro (Sul)")
    cidade = models.CharField(max_length=100, default="Teresina - PI")
    cep = models.CharField(max_length=20, default="64001-280")
    telefone = models.CharField(max_length=50, default="(86) 3221-3021")
    email = models.EmailField(blank=True)
    horario_livraria = models.CharField(max_length=200, default="Segunda à Sábado")
    
    # Singleton: garante que só existe 1 registo
    def save(self, *args, **kwargs):
        if not self.pk and InformacaoContato.objects.exists():
            return
        super(InformacaoContato, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Configuração de Contato"
        verbose_name_plural = "Configuração de Contato"

    def __str__(self):
        return "Dados de Contato da FEPI"

# --- NOVOS MODELOS DE ESTRUTURA ---

class TipoDiretoria(models.Model):
    """ Define o grupo hierárquico: Diretoria Executiva, Conselho Fiscal, DIJ, ESDE, etc. """
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
    """ Define o cargo específico: Presidente, Secretário, Coordenador, Conselheiro. """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Cargo")

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Cargo Presidência e Departamentos"
        verbose_name_plural = "Cargos Presidência e Departamentos"
        ordering = ['nome']


# 2. Página Institucional (Texto e História)
class PaginaInstitucional(models.Model):
    """ Conteúdo Fixo da página Institucional + Ano da Gestão """
    titulo = models.CharField(max_length=200, default="Nossa História")
    conteudo = RichTextField(verbose_name="Texto da História") # CKEditor
    frase_destaque = models.CharField(max_length=300, verbose_name="Frase de Destaque (Missão)", blank=True)
    
    # Gestão Anual
    ano_inicio = models.IntegerField(default=2024, verbose_name="Ano Início da Gestão")
    ano_fim = models.IntegerField(default=2027, verbose_name="Ano Fim da Gestão")
    
    # Singleton
    def save(self, *args, **kwargs):
        if not self.pk and PaginaInstitucional.objects.exists(): return
        super(PaginaInstitucional, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Página Institucional (Texto)"
        verbose_name_plural = "Página Institucional (Texto)"

    def __str__(self):
        return f"Configuração da Página Principal ({self.ano_inicio}-{self.ano_fim})"


class MembroDiretoria(models.Model):
    """ Membro específico (Responsáveis por Departamento) """
    nome = models.CharField(max_length=200, verbose_name="Nome do Responsável")
    
    # Foreign Keys para as tabelas dinâmicas
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, verbose_name="Cargo")
    tipo = models.ForeignKey(TipoDiretoria, on_delete=models.PROTECT, verbose_name="Tipo/Departamento")
    
    # Informações de Contato
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, verbose_name="Email")

    ordem = models.IntegerField(default=0, help_text="Para ordenar dentro do Tipo/Departamento")

    class Meta:
        verbose_name = "Membro/Responsável"
        verbose_name_plural = "Membros e Responsáveis"
        ordering = ['tipo__ordem', 'ordem', 'nome']
    
    def __str__(self):
        return f"{self.cargo.nome} ({self.nome})"


# 4. Configuração da Home (Banner, YouTube e Pop-up)
class ConfiguracaoHome(models.Model):
    # --- BANNER PRINCIPAL ---
    titulo_banner = models.CharField(max_length=200, default="Federação Espírita do Piauí")
    subtitulo_banner = models.CharField(max_length=300, default="Unindo corações, esclarecendo mentes e consolando almas.")
    imagem_banner = models.ImageField(upload_to='banners/', blank=True, null=True, help_text="Imagem de fundo do topo (Opcional)")
    
    # --- YOUTUBE ---
    youtube_video_id = models.CharField(max_length=50, help_text="Apenas o código do vídeo (ex: se o link é youtube.com/watch?v=ABC1234, cole ABC1234)", default="SEU_ID_AQUI")
    
    # --- POP-UP MODAL (MARKETING) ---
    popup_ativo = models.BooleanField(default=False, verbose_name="Ativar Pop-up?")
    popup_titulo = models.CharField(max_length=100, blank=True, verbose_name="Título do Pop-up")
    popup_imagem = models.ImageField(upload_to='popup/', blank=True, null=True, verbose_name="Imagem do Pop-up")
    popup_link = models.URLField(blank=True, verbose_name="Link de Destino (Notícia/Curso)")
    popup_botao_texto = models.CharField(max_length=50, default="Saiba Mais", verbose_name="Texto do Botão")
    
    # Datas de Vigência do Pop-up
    popup_inicio = models.DateTimeField(default=timezone.now, verbose_name="Início da Exibição")
    popup_fim = models.DateTimeField(default=timezone.now, verbose_name="Fim da Exibição")

    # Singleton
    def save(self, *args, **kwargs):
        if not self.pk and ConfiguracaoHome.objects.exists():
            return
        super(ConfiguracaoHome, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Configuração da Home (Banner/Pop-up)"
        verbose_name_plural = "Configuração da Home (Banner/Pop-up)"
    
    def __str__(self):
        return "Configuração da Página Inicial"

# 4.1 Configuração do YouTube (separado da Home)
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

    # Singleton
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