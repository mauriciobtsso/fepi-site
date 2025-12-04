from django.db import models

class AtividadeSemanal(models.Model):
    DIAS = (
        ('SEG', 'Segunda-feira'),
        ('TER', 'Terça-feira'),
        ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'),
        ('SEX', 'Sexta-feira'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
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
        ordering = ['dia', 'horario'] # Isso pode precisar de ajuste manual na ordem, mas serve por agora

class Doutrinaria(models.Model):
    tema = models.CharField(max_length=200)
    palestrante = models.CharField(max_length=200)
    data_hora = models.DateTimeField(verbose_name="Data e Hora")
    imagem = models.ImageField(upload_to='doutrinarias/', verbose_name="Foto de Divulgação (Instagram)")
    descricao = models.TextField(blank=True, verbose_name="Detalhes")

    def __str__(self):
        return f"{self.data_hora.strftime('%d/%m')} - {self.tema}"

    class Meta:
        verbose_name = "Palestra Doutrinária"
        verbose_name_plural = "Doutrinárias (Agenda)"
        ordering = ['data_hora']