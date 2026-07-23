
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_favorito'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservahospedaje',
            name='fecha_reserva',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='reservahospedaje',
            name='metodo_pago',
            field=models.CharField(blank=True, choices=[('tarjeta', 'Tarjeta de crédito/débito'), ('transferencia', 'Transferencia bancaria'), ('efectivo', 'Efectivo')], max_length=20, null=True),
        ),
    ]
