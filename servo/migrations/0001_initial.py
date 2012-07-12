# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tag'
        db.create_table('servo_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='Uusi tagi', max_length=255)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('times_used', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('servo', ['Tag'])

        # Adding model 'Attachment'
        db.create_table('servo_attachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Uusi tiedosto', max_length=255)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('uploaded_by', self.gf('django.db.models.fields.CharField')(default='filipp', max_length=32)),
            ('uploaded_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 12, 0, 0))),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 12, 0, 0))),
            ('content', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('is_template', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('servo', ['Attachment'])

        # Adding M2M table for field tags on 'Attachment'
        db.create_table('servo_attachment_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('attachment', models.ForeignKey(orm['servo.attachment'], null=False)),
            ('tag', models.ForeignKey(orm['servo.tag'], null=False))
        ))
        db.create_unique('servo_attachment_tags', ['attachment_id', 'tag_id'])

        # Adding model 'Configuration'
        db.create_table('servo_configuration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pct_margin', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=4, decimal_places=2)),
            ('pct_vat', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=4, decimal_places=2)),
            ('encryption_key', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('mail_from', self.gf('django.db.models.fields.EmailField')(default='servo@example.com', max_length=75)),
            ('imap_host', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('imap_user', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('imap_password', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('imap_ssl', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('smtp_host', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('sms_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sms_user', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('sms_password', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('servo', ['Configuration'])

        # Adding model 'Property'
        db.create_table('servo_property', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('format', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('servo', ['Property'])

        # Adding model 'Customer'
        db.create_table('servo_customer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Uusi asiakas', max_length=255)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('servo', ['Customer'])

        # Adding model 'ContactInfo'
        db.create_table('servo_contactinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Customer'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('servo', ['ContactInfo'])

        # Adding model 'Location'
        db.create_table('servo_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='Uusi sijainti', max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('shipto', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('servo', ['Location'])

        # Adding model 'Article'
        db.create_table('servo_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='Uusi artikkeli', max_length=255)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('tags', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 12, 0, 0))),
        ))
        db.send_create_signal('servo', ['Article'])

        # Adding M2M table for field attachments on 'Article'
        db.create_table('servo_article_attachments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['servo.article'], null=False)),
            ('attachment', models.ForeignKey(orm['servo.attachment'], null=False))
        ))
        db.create_unique('servo_article_attachments', ['article_id', 'attachment_id'])

        # Adding model 'Spec'
        db.create_table('servo_spec', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('path', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('servo', ['Spec'])

        # Adding model 'SpecInfo'
        db.create_table('servo_specinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('spec', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Spec'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('servo', ['SpecInfo'])

        # Adding model 'Device'
        db.create_table('servo_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('purchased_on', self.gf('django.db.models.fields.DateField')(blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('spec', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Spec'], null=True)),
        ))
        db.send_create_signal('servo', ['Device'])

        # Adding model 'Product'
        db.create_table('servo_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='Uusi tuote', max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=32)),
            ('pct_vat', self.gf('django.db.models.fields.DecimalField')(default='23.00', max_digits=4, decimal_places=2)),
            ('pct_margin', self.gf('django.db.models.fields.DecimalField')(default='25.00', max_digits=4, decimal_places=2)),
            ('price_notax', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('price_sales', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('price_purchase', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('price_exchange', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('is_serialized', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('warranty_period', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('shelf', self.gf('django.db.models.fields.CharField')(default='', max_length=8, blank=True)),
            ('brand', self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True)),
            ('amount_minimum', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('servo', ['Product'])

        # Adding M2M table for field tags on 'Product'
        db.create_table('servo_product_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm['servo.product'], null=False)),
            ('tag', models.ForeignKey(orm['servo.tag'], null=False))
        ))
        db.create_unique('servo_product_tags', ['product_id', 'tag_id'])

        # Adding M2M table for field specs on 'Product'
        db.create_table('servo_product_specs', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm['servo.product'], null=False)),
            ('spec', models.ForeignKey(orm['servo.spec'], null=False))
        ))
        db.create_unique('servo_product_specs', ['product_id', 'spec_id'])

        # Adding M2M table for field attachments on 'Product'
        db.create_table('servo_product_attachments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm['servo.product'], null=False)),
            ('attachment', models.ForeignKey(orm['servo.attachment'], null=False))
        ))
        db.create_unique('servo_product_attachments', ['product_id', 'attachment_id'])

        # Adding model 'GsxData'
        db.create_table('servo_gsxdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('value', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('references', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('reference_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('servo', ['GsxData'])

        # Adding model 'GsxRepair'
        db.create_table('servo_gsxrepair', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('symptom', self.gf('django.db.models.fields.TextField')()),
            ('diagnosis', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('servo', ['GsxRepair'])

        # Adding model 'Calendar'
        db.create_table('servo_calendar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='Uusi kalenteri', max_length=128)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('hours', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('servo', ['Calendar'])

        # Adding model 'CalendarEvent'
        db.create_table('servo_calendarevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('started_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 12, 0, 0))),
            ('finished_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('hours', self.gf('django.db.models.fields.IntegerField')(default=8)),
            ('calendar', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Calendar'])),
        ))
        db.send_create_signal('servo', ['CalendarEvent'])

        # Adding model 'Invoice'
        db.create_table('servo_invoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 12, 0, 0))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('paid_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('payment_method', self.gf('django.db.models.fields.CharField')(default=(0, u'Ei veloitusta'), max_length=128)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Customer'])),
            ('customer_info', self.gf('django.db.models.fields.TextField')()),
            ('total_tax', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('total_margin', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('total_sum', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
        ))
        db.send_create_signal('servo', ['Invoice'])

        # Adding model 'InvoiceItem'
        db.create_table('servo_invoiceitem', (
            ('product_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['servo.Product'], unique=True, primary_key=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Invoice'])),
        ))
        db.send_create_signal('servo', ['InvoiceItem'])

        # Adding model 'PurchaseOrder'
        db.create_table('servo_purchaseorder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('confirmation', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('dispatch_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('sales_order', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 12, 0, 0))),
            ('date_ordered', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 12, 0, 0))),
            ('date_arrived', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('carrier', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('supplier', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('tracking_id', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('days_delivered', self.gf('django.db.models.fields.IntegerField')(blank=True)),
        ))
        db.send_create_signal('servo', ['PurchaseOrder'])

        # Adding model 'Inventory'
        db.create_table('servo_inventory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slot', self.gf('django.db.models.fields.IntegerField')()),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Product'])),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('servo', ['Inventory'])

        # Adding model 'GsxAccount'
        db.create_table('servo_gsxaccount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='Uusi tili', max_length=128)),
            ('sold_to', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('ship_to', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('environment', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('is_default', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('servo', ['GsxAccount'])

        # Adding model 'Status'
        db.create_table('servo_status', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='Uusi status', max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('limit_green', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('limit_yellow', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('limit_factor', self.gf('django.db.models.fields.IntegerField')(default=('60', 'Minuuttia'))),
        ))
        db.send_create_signal('servo', ['Status'])

        # Adding model 'Queue'
        db.create_table('servo_queue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='Uusi jono', max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('gsx_account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.GsxAccount'], null=True)),
            ('order_template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='order_template', null=True, to=orm['servo.Attachment'])),
            ('receipt_template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='receipt_template', null=True, to=orm['servo.Attachment'])),
            ('dispatch_template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dispatch_template', null=True, to=orm['servo.Attachment'])),
        ))
        db.send_create_signal('servo', ['Queue'])

        # Adding model 'QueueStatus'
        db.create_table('servo_queuestatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('limit_green', self.gf('django.db.models.fields.IntegerField')()),
            ('limit_yellow', self.gf('django.db.models.fields.IntegerField')()),
            ('limit_factor', self.gf('django.db.models.fields.IntegerField')()),
            ('queue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Queue'])),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Status'])),
        ))
        db.send_create_signal('servo', ['QueueStatus'])

        # Adding model 'Order'
        db.create_table('servo_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 12, 0, 0))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_by', to=orm['auth.User'])),
            ('closed_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Customer'], null=True)),
            ('queue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Queue'], null=True)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Status'], null=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=16)),
            ('status_limit_green', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('status_limit_yellow', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('dispatch_method', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('servo', ['Order'])

        # Adding M2M table for field followed_by on 'Order'
        db.create_table('servo_order_followed_by', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('order', models.ForeignKey(orm['servo.order'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('servo_order_followed_by', ['order_id', 'user_id'])

        # Adding M2M table for field tags on 'Order'
        db.create_table('servo_order_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('order', models.ForeignKey(orm['servo.order'], null=False)),
            ('tag', models.ForeignKey(orm['servo.tag'], null=False))
        ))
        db.create_unique('servo_order_tags', ['order_id', 'tag_id'])

        # Adding M2M table for field devices on 'Order'
        db.create_table('servo_order_devices', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('order', models.ForeignKey(orm['servo.order'], null=False)),
            ('device', models.ForeignKey(orm['servo.device'], null=False))
        ))
        db.create_unique('servo_order_devices', ['order_id', 'device_id'])

        # Adding M2M table for field attachments on 'Order'
        db.create_table('servo_order_attachments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('order', models.ForeignKey(orm['servo.order'], null=False)),
            ('attachment', models.ForeignKey(orm['servo.attachment'], null=False))
        ))
        db.create_unique('servo_order_attachments', ['order_id', 'attachment_id'])

        # Adding model 'PurchaseOrderItem'
        db.create_table('servo_purchaseorderitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('service_order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Order'], null=True)),
            ('purchase_order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.PurchaseOrder'])),
        ))
        db.send_create_signal('servo', ['PurchaseOrderItem'])

        # Adding model 'Event'
        db.create_table('servo_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 12, 0, 0))),
            ('handled_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Order'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('servo', ['Event'])

        # Adding model 'Issue'
        db.create_table('servo_issue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('symptom', self.gf('django.db.models.fields.TextField')()),
            ('diagnosis', self.gf('django.db.models.fields.TextField')()),
            ('solution', self.gf('django.db.models.fields.TextField')()),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 12, 0, 0))),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Order'])),
        ))
        db.send_create_signal('servo', ['Issue'])

        # Adding model 'Message'
        db.create_table('servo_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mailfrom', self.gf('django.db.models.fields.EmailField')(default='', max_length=75, blank=True)),
            ('smsfrom', self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True)),
            ('mailto', self.gf('django.db.models.fields.EmailField')(default='', max_length=75, blank=True)),
            ('smsto', self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sender', to=orm['auth.User'])),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recipient', null=True, to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 12, 0, 0))),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Order'], null=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('flags', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('is_template', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('servo', ['Message'])

        # Adding M2M table for field attachments on 'Message'
        db.create_table('servo_message_attachments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('message', models.ForeignKey(orm['servo.message'], null=False)),
            ('attachment', models.ForeignKey(orm['servo.attachment'], null=False))
        ))
        db.create_unique('servo_message_attachments', ['message_id', 'attachment_id'])

        # Adding model 'OrderItem'
        db.create_table('servo_orderitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='Uusi tuote', max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=32)),
            ('pct_vat', self.gf('django.db.models.fields.DecimalField')(default='23.00', max_digits=4, decimal_places=2)),
            ('pct_margin', self.gf('django.db.models.fields.DecimalField')(default='25.00', max_digits=4, decimal_places=2)),
            ('price_notax', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('price_sales', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('price_purchase', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('price_exchange', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('is_serialized', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Order'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Product'])),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('reported', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('servo', ['OrderItem'])

        # Adding model 'Search'
        db.create_table('servo_search', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query', self.gf('django.db.models.fields.TextField')()),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('shared', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('servo', ['Search'])

        # Adding model 'UserProfile'
        db.create_table('servo_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('tech_id', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Location'])),
            ('locale', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal('servo', ['UserProfile'])


    def backwards(self, orm):
        # Deleting model 'Tag'
        db.delete_table('servo_tag')

        # Deleting model 'Attachment'
        db.delete_table('servo_attachment')

        # Removing M2M table for field tags on 'Attachment'
        db.delete_table('servo_attachment_tags')

        # Deleting model 'Configuration'
        db.delete_table('servo_configuration')

        # Deleting model 'Property'
        db.delete_table('servo_property')

        # Deleting model 'Customer'
        db.delete_table('servo_customer')

        # Deleting model 'ContactInfo'
        db.delete_table('servo_contactinfo')

        # Deleting model 'Location'
        db.delete_table('servo_location')

        # Deleting model 'Article'
        db.delete_table('servo_article')

        # Removing M2M table for field attachments on 'Article'
        db.delete_table('servo_article_attachments')

        # Deleting model 'Spec'
        db.delete_table('servo_spec')

        # Deleting model 'SpecInfo'
        db.delete_table('servo_specinfo')

        # Deleting model 'Device'
        db.delete_table('servo_device')

        # Deleting model 'Product'
        db.delete_table('servo_product')

        # Removing M2M table for field tags on 'Product'
        db.delete_table('servo_product_tags')

        # Removing M2M table for field specs on 'Product'
        db.delete_table('servo_product_specs')

        # Removing M2M table for field attachments on 'Product'
        db.delete_table('servo_product_attachments')

        # Deleting model 'GsxData'
        db.delete_table('servo_gsxdata')

        # Deleting model 'GsxRepair'
        db.delete_table('servo_gsxrepair')

        # Deleting model 'Calendar'
        db.delete_table('servo_calendar')

        # Deleting model 'CalendarEvent'
        db.delete_table('servo_calendarevent')

        # Deleting model 'Invoice'
        db.delete_table('servo_invoice')

        # Deleting model 'InvoiceItem'
        db.delete_table('servo_invoiceitem')

        # Deleting model 'PurchaseOrder'
        db.delete_table('servo_purchaseorder')

        # Deleting model 'Inventory'
        db.delete_table('servo_inventory')

        # Deleting model 'GsxAccount'
        db.delete_table('servo_gsxaccount')

        # Deleting model 'Status'
        db.delete_table('servo_status')

        # Deleting model 'Queue'
        db.delete_table('servo_queue')

        # Deleting model 'QueueStatus'
        db.delete_table('servo_queuestatus')

        # Deleting model 'Order'
        db.delete_table('servo_order')

        # Removing M2M table for field followed_by on 'Order'
        db.delete_table('servo_order_followed_by')

        # Removing M2M table for field tags on 'Order'
        db.delete_table('servo_order_tags')

        # Removing M2M table for field devices on 'Order'
        db.delete_table('servo_order_devices')

        # Removing M2M table for field attachments on 'Order'
        db.delete_table('servo_order_attachments')

        # Deleting model 'PurchaseOrderItem'
        db.delete_table('servo_purchaseorderitem')

        # Deleting model 'Event'
        db.delete_table('servo_event')

        # Deleting model 'Issue'
        db.delete_table('servo_issue')

        # Deleting model 'Message'
        db.delete_table('servo_message')

        # Removing M2M table for field attachments on 'Message'
        db.delete_table('servo_message_attachments')

        # Deleting model 'OrderItem'
        db.delete_table('servo_orderitem')

        # Deleting model 'Search'
        db.delete_table('servo_search')

        # Deleting model 'UserProfile'
        db.delete_table('servo_userprofile')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'servo.article': {
            'Meta': {'object_name': 'Article'},
            'attachments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Attachment']", 'symmetrical': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 12, 0, 0)'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tags': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Uusi artikkeli'", 'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {})
        },
        'servo.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'content': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_template': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Uusi tiedosto'", 'max_length': '255'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Tag']", 'symmetrical': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 12, 0, 0)'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 12, 0, 0)'}),
            'uploaded_by': ('django.db.models.fields.CharField', [], {'default': "'filipp'", 'max_length': '32'})
        },
        'servo.calendar': {
            'Meta': {'object_name': 'Calendar'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Uusi kalenteri'", 'max_length': '128'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'servo.calendarevent': {
            'Meta': {'object_name': 'CalendarEvent'},
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Calendar']"}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'finished_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 12, 0, 0)'})
        },
        'servo.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'encryption_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imap_host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'imap_password': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'imap_ssl': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'imap_user': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'mail_from': ('django.db.models.fields.EmailField', [], {'default': "'servo@example.com'", 'max_length': '75'}),
            'pct_margin': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '4', 'decimal_places': '2'}),
            'pct_vat': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '4', 'decimal_places': '2'}),
            'sms_password': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sms_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sms_user': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'smtp_host': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'servo.contactinfo': {
            'Meta': {'object_name': 'ContactInfo'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'servo.customer': {
            'Meta': {'object_name': 'Customer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Uusi asiakas'", 'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'servo.device': {
            'Meta': {'object_name': 'Device'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'purchased_on': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'spec': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Spec']", 'null': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        'servo.event': {
            'Meta': {'object_name': 'Event'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 12, 0, 0)'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'handled_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Order']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'servo.gsxaccount': {
            'Meta': {'object_name': 'GsxAccount'},
            'environment': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'ship_to': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sold_to': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Uusi tili'", 'max_length': '128'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'servo.gsxdata': {
            'Meta': {'object_name': 'GsxData'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'reference_id': ('django.db.models.fields.IntegerField', [], {}),
            'references': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'servo.gsxrepair': {
            'Meta': {'object_name': 'GsxRepair'},
            'diagnosis': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'symptom': ('django.db.models.fields.TextField', [], {})
        },
        'servo.inventory': {
            'Meta': {'object_name': 'Inventory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Product']"}),
            'slot': ('django.db.models.fields.IntegerField', [], {}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'servo.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 12, 0, 0)'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Customer']"}),
            'customer_info': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid_at': ('django.db.models.fields.DateTimeField', [], {}),
            'payment_method': ('django.db.models.fields.CharField', [], {'default': "(0, u'Ei veloitusta')", 'max_length': '128'}),
            'total_margin': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'total_sum': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'total_tax': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'})
        },
        'servo.invoiceitem': {
            'Meta': {'ordering': "['-id']", 'object_name': 'InvoiceItem', '_ormbases': ['servo.Product']},
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Invoice']"}),
            'product_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['servo.Product']", 'unique': 'True', 'primary_key': 'True'})
        },
        'servo.issue': {
            'Meta': {'ordering': "['id']", 'object_name': 'Issue'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 12, 0, 0)'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'diagnosis': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Order']"}),
            'solution': ('django.db.models.fields.TextField', [], {}),
            'symptom': ('django.db.models.fields.TextField', [], {})
        },
        'servo.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'shipto': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Uusi sijainti'", 'max_length': '255'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'servo.message': {
            'Meta': {'ordering': "['id']", 'object_name': 'Message'},
            'attachments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Attachment']", 'symmetrical': 'False'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 12, 0, 0)'}),
            'flags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_template': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mailfrom': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'mailto': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Order']", 'null': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recipient'", 'null': 'True', 'to': "orm['auth.User']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sender'", 'to': "orm['auth.User']"}),
            'smsfrom': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'smsto': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'servo.order': {
            'Meta': {'ordering': "['-priority', 'id']", 'object_name': 'Order'},
            'attachments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Attachment']", 'symmetrical': 'False'}),
            'closed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 12, 0, 0)'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_by'", 'to': "orm['auth.User']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Customer']", 'null': 'True'}),
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Device']", 'symmetrical': 'False'}),
            'dispatch_method': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'followed_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'followed_by'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Product']", 'through': "orm['servo.OrderItem']", 'symmetrical': 'False'}),
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Queue']", 'null': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '16'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Status']", 'null': 'True'}),
            'status_limit_green': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'status_limit_yellow': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Tag']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'servo.orderitem': {
            'Meta': {'ordering': "['-id']", 'object_name': 'OrderItem'},
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '32'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_serialized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Order']"}),
            'pct_margin': ('django.db.models.fields.DecimalField', [], {'default': "'25.00'", 'max_digits': '4', 'decimal_places': '2'}),
            'pct_vat': ('django.db.models.fields.DecimalField', [], {'default': "'23.00'", 'max_digits': '4', 'decimal_places': '2'}),
            'price_exchange': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'price_notax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'price_purchase': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'price_sales': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Product']"}),
            'reported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Uusi tuote'", 'max_length': '255'})
        },
        'servo.product': {
            'Meta': {'object_name': 'Product'},
            'amount_minimum': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'attachments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Attachment']", 'symmetrical': 'False', 'blank': 'True'}),
            'brand': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '32'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_serialized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pct_margin': ('django.db.models.fields.DecimalField', [], {'default': "'25.00'", 'max_digits': '4', 'decimal_places': '2'}),
            'pct_vat': ('django.db.models.fields.DecimalField', [], {'default': "'23.00'", 'max_digits': '4', 'decimal_places': '2'}),
            'price_exchange': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'price_notax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'price_purchase': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'price_sales': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'shelf': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '8', 'blank': 'True'}),
            'specs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Spec']", 'symmetrical': 'False', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Uusi tuote'", 'max_length': '255'}),
            'warranty_period': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'servo.property': {
            'Meta': {'object_name': 'Property'},
            'format': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'servo.purchaseorder': {
            'Meta': {'object_name': 'PurchaseOrder'},
            'carrier': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'confirmation': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'date_arrived': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 12, 0, 0)'}),
            'date_ordered': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 12, 0, 0)'}),
            'days_delivered': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'dispatch_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sales_order': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'supplier': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'tracking_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'servo.purchaseorderitem': {
            'Meta': {'object_name': 'PurchaseOrderItem'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'purchase_order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.PurchaseOrder']"}),
            'service_order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Order']", 'null': 'True'})
        },
        'servo.queue': {
            'Meta': {'object_name': 'Queue'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dispatch_template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dispatch_template'", 'null': 'True', 'to': "orm['servo.Attachment']"}),
            'gsx_account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.GsxAccount']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_template'", 'null': 'True', 'to': "orm['servo.Attachment']"}),
            'receipt_template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'receipt_template'", 'null': 'True', 'to': "orm['servo.Attachment']"}),
            'statuses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Status']", 'through': "orm['servo.QueueStatus']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Uusi jono'", 'max_length': '255'})
        },
        'servo.queuestatus': {
            'Meta': {'object_name': 'QueueStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_factor': ('django.db.models.fields.IntegerField', [], {}),
            'limit_green': ('django.db.models.fields.IntegerField', [], {}),
            'limit_yellow': ('django.db.models.fields.IntegerField', [], {}),
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Queue']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Status']"})
        },
        'servo.search': {
            'Meta': {'object_name': 'Search'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'query': ('django.db.models.fields.TextField', [], {}),
            'shared': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'servo.spec': {
            'Meta': {'object_name': 'Spec'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'servo.specinfo': {
            'Meta': {'object_name': 'SpecInfo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'spec': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Spec']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'servo.status': {
            'Meta': {'object_name': 'Status'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_factor': ('django.db.models.fields.IntegerField', [], {'default': "('60', 'Minuuttia')"}),
            'limit_green': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'limit_yellow': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Uusi status'", 'max_length': '255'})
        },
        'servo.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'times_used': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Uusi tagi'", 'max_length': '255'})
        },
        'servo.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Location']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'tech_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['servo']