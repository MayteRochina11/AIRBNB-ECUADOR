
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_reservahospedaje_fecha_reserva_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='agente',
            name='nombre',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
