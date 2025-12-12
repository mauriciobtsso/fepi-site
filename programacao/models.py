from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify

class AtividadeSemanal(models.Model):
    DIAS = (
        ('SEG', 'Segunda-feira'), ('TER', 'Terça-feira'), ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'), ('SEX', 'Sexta-feira'), ('SAB', 'Sábado'), ('DOM', 'Domingo'),
    )
    dia = models.CharField(max_length=3, choices=DIAS, verbose_name="Dia da Semana")
    horario = models.CharField(max_length=50, verbose_name="Horário (ex: 15h às 17h)")
    nome = models.CharField(max_length=200, verbose_name="Nome da Atividade")
    descricao = models.TextField(blank=True, verbose_name="Descrição / Sub-atividades")
    
    def __str__(self):
        return f"{self.get_dia_display()} - {self.nome}"
    class Meta:
        verbose_name = "Atividade Semanal"
        verbose_name_plural = "Atividades Semanais"
        ordering = ['dia', 'horario']

class Doutrinaria(models.Model):
    tema = models.CharField(max_length=200)
    palestrante = models.CharField(max_length=200)
    data_hora = models.DateTimeField(verbose_name="Data e Hora")
    imagem = models.ImageField(upload_to='doutrinarias/', verbose_name="Foto de Divulgação")
    descricao = RichTextField(blank=True, verbose_name="Detalhes")

    def __str__(self):
        return f"{self.data_hora.strftime('%d/%m')} - {self.tema}"
    class Meta:
        verbose_name = "Palestra Doutrinária"
        verbose_name_plural = "Doutrinárias (Agenda)"
        ordering = ['data_hora']

class CursoEvento(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Nome do Evento/Curso")
    
    # NOVO CAMPO SLUG
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Link Amigável")

    data_evento = models.DateTimeField(verbose_name="Data e Horário")
    local = models.CharField(max_length=200, default="Sede da FEPI", verbose_name="Local")
    imagem = models.ImageField(upload_to='cursos/', verbose_name="Cartaz de Divulgação")
    descricao = RichTextField(verbose_name="Descrição Detalhada")
    link_inscricao = models.URLField(blank=True, null=True, verbose_name="Link para Inscrição (Forms/Whats)")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.data_evento.strftime('%d/%m')} - {self.titulo}"

    class Meta:
        verbose_name = "Curso ou Evento Especial"
        verbose_name_plural = "Cursos & Eventos"
        ordering = ['data_evento']