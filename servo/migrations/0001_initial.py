# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GsxAccount'
        db.create_table('servo_gsxaccount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Uusi tili', max_length=128)),
            ('sold_to', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('ship_to', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('environment', self.gf('django.db.models.fields.CharField')(default=('pr', u'Tuotanto'), max_length=3)),
            ('is_default', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('servo', ['GsxAccount'])

        # Adding model 'Label'
        db.create_table('servo_label', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('servo', ['Label'])

        # Adding model 'Tag'
        db.create_table('servo_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Uusi tagi', unique=True, max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('times_used', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['servo.Tag'])),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('servo', ['Tag'])

        # Adding model 'Attachment'
        db.create_table('servo_attachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=u'Uusi tiedosto', max_length=255)),
            ('uploaded_by', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('uploaded_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 14, 0, 0))),
            ('content', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('servo', ['Attachment'])

        # Adding model 'Location'
        db.create_table('servo_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Uusi toimipaikka', max_length=255)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('ship_to', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('country', self.gf('django_countries.fields.CountryField')(max_length=2)),
            ('office_hours', self.gf('django.db.models.fields.CharField')(default='9:00 - 18:00', max_length=16, null=True, blank=True)),
        ))
        db.send_create_signal('servo', ['Location'])

        # Adding model 'Place'
        db.create_table('servo_place', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Location'])),
        ))
        db.send_create_signal('servo', ['Place'])

        # Adding model 'Configuration'
        db.create_table('servo_configuration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('servo', ['Configuration'])

        # Adding model 'Property'
        db.create_table('servo_property', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Uusi kentt\xe4', max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(default=('customer', u'Asiakas'), max_length=32)),
            ('format', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('servo', ['Property'])

        # Adding model 'Article'
        db.create_table('servo_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Uusi artikkeli', unique=True, max_length=255)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 14, 0, 0))),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 14, 0, 0))),
        ))
        db.send_create_signal('servo', ['Article'])

        # Adding M2M table for field attachments on 'Article'
        db.create_table('servo_article_attachments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['servo.article'], null=False)),
            ('attachment', models.ForeignKey(orm['servo.attachment'], null=False))
        ))
        db.create_unique('servo_article_attachments', ['article_id', 'attachment_id'])

        # Adding M2M table for field tags on 'Article'
        db.create_table('servo_article_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['servo.article'], null=False)),
            ('tag', models.ForeignKey(orm['servo.tag'], null=False))
        ))
        db.create_unique('servo_article_tags', ['article_id', 'tag_id'])

        # Adding model 'Search'
        db.create_table('servo_search', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query', self.gf('django.db.models.fields.TextField')()),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('shared', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('servo', ['Search'])

        # Adding model 'Event'
        db.create_table('servo_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('triggered_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('triggered_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 14, 0, 0))),
            ('handled_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('ref', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('ref_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('servo', ['Event'])

        # Adding model 'Notification'
        db.create_table('servo_notification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('servo', ['Notification'])

        # Adding model 'Template'
        db.create_table('servo_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Uusi pohja', max_length=128)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('servo', ['Template'])

        # Adding model 'Queue'
        db.create_table('servo_queue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Uusi jono', unique=True, max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('gsx_account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.GsxAccount'], null=True, blank=True)),
            ('default_status', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='default_status', null=True, to=orm['servo.Status'])),
            ('order_template', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('receipt_template', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('dispatch_template', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('servo', ['Queue'])

        # Adding model 'Status'
        db.create_table('servo_status', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Uusi status', unique=True, max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('limit_green', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('limit_yellow', self.gf('django.db.models.fields.IntegerField')(default=15)),
            ('limit_factor', self.gf('django.db.models.fields.IntegerField')(default=(60, u'Minuuttia'))),
        ))
        db.send_create_signal('servo', ['Status'])

        # Adding model 'QueueStatus'
        db.create_table('servo_queuestatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('queue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Queue'])),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Status'])),
            ('idx', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('limit_green', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('limit_yellow', self.gf('django.db.models.fields.IntegerField')(default=15)),
            ('limit_factor', self.gf('django.db.models.fields.IntegerField')(default=(60, u'Minuuttia'))),
        ))
        db.send_create_signal('servo', ['QueueStatus'])

        # Adding model 'UserProfile'
        db.create_table('servo_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Location'], null=True)),
            ('tech_id', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('locale', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('servo', ['UserProfile'])

        # Adding M2M table for field queues on 'UserProfile'
        db.create_table('servo_userprofile_queues', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['servo.userprofile'], null=False)),
            ('queue', models.ForeignKey(orm['servo.queue'], null=False))
        ))
        db.create_unique('servo_userprofile_queues', ['userprofile_id', 'queue_id'])

        # Adding model 'Calendar'
        db.create_table('servo_calendar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Uusi kalenteri', max_length=128)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('hours', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('servo', ['Calendar'])

        # Adding model 'CalendarEvent'
        db.create_table('servo_calendarevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('started_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 14, 0, 0))),
            ('finished_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('hours', self.gf('django.db.models.fields.IntegerField')(default=8)),
            ('calendar', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Calendar'])),
        ))
        db.send_create_signal('servo', ['CalendarEvent'])

        # Adding model 'Device'
        db.create_table('servo_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(default=u'Uusi laite', max_length=128)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('purchased_on', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('servo', ['Device'])

        # Adding M2M table for field tags on 'Device'
        db.create_table('servo_device_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('device', models.ForeignKey(orm['servo.device'], null=False)),
            ('tag', models.ForeignKey(orm['servo.tag'], null=False))
        ))
        db.create_unique('servo_device_tags', ['device_id', 'tag_id'])

        # Adding M2M table for field files on 'Device'
        db.create_table('servo_device_files', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('device', models.ForeignKey(orm['servo.device'], null=False)),
            ('attachment', models.ForeignKey(orm['servo.attachment'], null=False))
        ))
        db.create_unique('servo_device_files', ['device_id', 'attachment_id'])

        # Adding model 'Customer'
        db.create_table('servo_customer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='contacts', null=True, to=orm['servo.Customer'])),
            ('name', self.gf('django.db.models.fields.CharField')(default=u'Uusi asiakas', max_length=255)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('street_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('is_company', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('servo', ['Customer'])

        # Adding M2M table for field tags on 'Customer'
        db.create_table('servo_customer_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customer', models.ForeignKey(orm['servo.customer'], null=False)),
            ('tag', models.ForeignKey(orm['servo.tag'], null=False))
        ))
        db.create_unique('servo_customer_tags', ['customer_id', 'tag_id'])

        # Adding M2M table for field devices on 'Customer'
        db.create_table('servo_customer_devices', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customer', models.ForeignKey(orm['servo.customer'], null=False)),
            ('device', models.ForeignKey(orm['servo.device'], null=False))
        ))
        db.create_unique('servo_customer_devices', ['customer_id', 'device_id'])

        # Adding model 'ContactInfo'
        db.create_table('servo_contactinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Customer'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('servo', ['ContactInfo'])

        # Adding model 'Product'
        db.create_table('servo_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=32, unique=True, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Uusi tuote', max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pct_vat', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=4, decimal_places=2)),
            ('pct_margin', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=4, decimal_places=2)),
            ('price_notax', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('price_sales', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('price_purchase', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('price_exchange', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
            ('is_serialized', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('warranty_period', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('shelf', self.gf('django.db.models.fields.CharField')(default='', max_length=8, blank=True)),
            ('brand', self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True)),
            ('component_code', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('amount_minimum', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('amount_reserved', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('amount_stocked', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('amount_ordered', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('shipping', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('servo', ['Product'])

        # Adding M2M table for field tags on 'Product'
        db.create_table('servo_product_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm['servo.product'], null=False)),
            ('tag', models.ForeignKey(orm['servo.tag'], null=False))
        ))
        db.create_unique('servo_product_tags', ['product_id', 'tag_id'])

        # Adding M2M table for field files on 'Product'
        db.create_table('servo_product_files', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm['servo.product'], null=False)),
            ('attachment', models.ForeignKey(orm['servo.attachment'], null=False))
        ))
        db.create_unique('servo_product_files', ['product_id', 'attachment_id'])

        # Adding model 'Inventory'
        db.create_table('servo_inventory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slot', self.gf('django.db.models.fields.IntegerField')()),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Product'])),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('servo', ['Inventory'])

        # Adding model 'Order'
        db.create_table('servo_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 14, 0, 0))),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_by', to=orm['auth.User'])),
            ('closed_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Location'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Customer'], null=True)),
            ('queue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Queue'], null=True)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.QueueStatus'], null=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=16)),
            ('status_limit_green', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('status_limit_yellow', self.gf('django.db.models.fields.IntegerField')(null=True)),
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

        # Adding model 'ServiceOrderItem'
        db.create_table('servo_serviceorderitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Product'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Order'])),
            ('dispatched', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('should_report', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('should_return', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('price_category', self.gf('django.db.models.fields.CharField')(default=('warranty', u'Takuu'), max_length=32)),
        ))
        db.send_create_signal('servo', ['ServiceOrderItem'])

        # Adding model 'Invoice'
        db.create_table('servo_invoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 14, 0, 0))),
            ('payment_method', self.gf('django.db.models.fields.IntegerField')(default=(0, u'Ei veloitusta'))),
            ('is_paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('paid_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Order'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Customer'], null=True, on_delete=models.SET_NULL)),
            ('customer_name', self.gf('django.db.models.fields.CharField')(default=u'K\xe4teisasiakas', max_length=128)),
            ('customer_phone', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('customer_email', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('customer_address', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('total_net', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('total_gross', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('total_tax', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('total_margin', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('servo', ['Invoice'])

        # Adding model 'InvoiceItem'
        db.create_table('servo_invoiceitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Product'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Invoice'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('servo', ['InvoiceItem'])

        # Adding model 'PurchaseOrder'
        db.create_table('servo_purchaseorder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sales_order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Order'], null=True, blank=True)),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('confirmation', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 14, 0, 0))),
            ('date_submitted', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('supplier', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('carrier', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('tracking_id', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('days_delivered', self.gf('django.db.models.fields.IntegerField')(default=1, blank=True)),
            ('has_arrived', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('servo', ['PurchaseOrder'])

        # Adding model 'PurchaseOrderItem'
        db.create_table('servo_purchaseorderitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Product'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('purchase_order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.PurchaseOrder'])),
            ('order_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.ServiceOrderItem'], null=True)),
            ('date_ordered', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('date_received', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('received_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal('servo', ['PurchaseOrderItem'])

        # Adding model 'Note'
        db.create_table('servo_note', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('code', self.gf('django.db.models.fields.CharField')(default='N5BJ46H', max_length=8)),
            ('sender', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('recipient', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(default=('note', u'Merkint\xe4'), max_length=10)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='replies', null=True, to=orm['servo.Note'])),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 14, 0, 0))),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['servo.Order'], null=True, blank=True)),
            ('flags', self.gf('django.db.models.fields.CharField')(default='01', max_length=2, blank=True)),
            ('should_report', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('servo', ['Note'])

        # Adding M2M table for field attachments on 'Note'
        db.create_table('servo_note_attachments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('note', models.ForeignKey(orm['servo.note'], null=False)),
            ('attachment', models.ForeignKey(orm['servo.attachment'], null=False))
        ))
        db.create_unique('servo_note_attachments', ['note_id', 'attachment_id'])


    def backwards(self, orm):
        # Deleting model 'GsxAccount'
        db.delete_table('servo_gsxaccount')

        # Deleting model 'Label'
        db.delete_table('servo_label')

        # Deleting model 'Tag'
        db.delete_table('servo_tag')

        # Deleting model 'Attachment'
        db.delete_table('servo_attachment')

        # Deleting model 'Location'
        db.delete_table('servo_location')

        # Deleting model 'Place'
        db.delete_table('servo_place')

        # Deleting model 'Configuration'
        db.delete_table('servo_configuration')

        # Deleting model 'Property'
        db.delete_table('servo_property')

        # Deleting model 'Article'
        db.delete_table('servo_article')

        # Removing M2M table for field attachments on 'Article'
        db.delete_table('servo_article_attachments')

        # Removing M2M table for field tags on 'Article'
        db.delete_table('servo_article_tags')

        # Deleting model 'Search'
        db.delete_table('servo_search')

        # Deleting model 'Event'
        db.delete_table('servo_event')

        # Deleting model 'Notification'
        db.delete_table('servo_notification')

        # Deleting model 'Template'
        db.delete_table('servo_template')

        # Deleting model 'Queue'
        db.delete_table('servo_queue')

        # Deleting model 'Status'
        db.delete_table('servo_status')

        # Deleting model 'QueueStatus'
        db.delete_table('servo_queuestatus')

        # Deleting model 'UserProfile'
        db.delete_table('servo_userprofile')

        # Removing M2M table for field queues on 'UserProfile'
        db.delete_table('servo_userprofile_queues')

        # Deleting model 'Calendar'
        db.delete_table('servo_calendar')

        # Deleting model 'CalendarEvent'
        db.delete_table('servo_calendarevent')

        # Deleting model 'Device'
        db.delete_table('servo_device')

        # Removing M2M table for field tags on 'Device'
        db.delete_table('servo_device_tags')

        # Removing M2M table for field files on 'Device'
        db.delete_table('servo_device_files')

        # Deleting model 'Customer'
        db.delete_table('servo_customer')

        # Removing M2M table for field tags on 'Customer'
        db.delete_table('servo_customer_tags')

        # Removing M2M table for field devices on 'Customer'
        db.delete_table('servo_customer_devices')

        # Deleting model 'ContactInfo'
        db.delete_table('servo_contactinfo')

        # Deleting model 'Product'
        db.delete_table('servo_product')

        # Removing M2M table for field tags on 'Product'
        db.delete_table('servo_product_tags')

        # Removing M2M table for field files on 'Product'
        db.delete_table('servo_product_files')

        # Deleting model 'Inventory'
        db.delete_table('servo_inventory')

        # Deleting model 'Order'
        db.delete_table('servo_order')

        # Removing M2M table for field followed_by on 'Order'
        db.delete_table('servo_order_followed_by')

        # Removing M2M table for field tags on 'Order'
        db.delete_table('servo_order_tags')

        # Removing M2M table for field devices on 'Order'
        db.delete_table('servo_order_devices')

        # Deleting model 'ServiceOrderItem'
        db.delete_table('servo_serviceorderitem')

        # Deleting model 'Invoice'
        db.delete_table('servo_invoice')

        # Deleting model 'InvoiceItem'
        db.delete_table('servo_invoiceitem')

        # Deleting model 'PurchaseOrder'
        db.delete_table('servo_purchaseorder')

        # Deleting model 'PurchaseOrderItem'
        db.delete_table('servo_purchaseorderitem')

        # Deleting model 'Note'
        db.delete_table('servo_note')

        # Removing M2M table for field attachments on 'Note'
        db.delete_table('servo_note_attachments')


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
            'Meta': {'ordering': "['-updated_at']", 'object_name': 'Article'},
            'attachments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['servo.Attachment']", 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 14, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['servo.Tag']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Uusi artikkeli'", 'unique': 'True', 'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 14, 0, 0)'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'servo.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'content': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u'Uusi tiedosto'", 'max_length': '255'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 14, 0, 0)'}),
            'uploaded_by': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'servo.calendar': {
            'Meta': {'object_name': 'Calendar'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Uusi kalenteri'", 'max_length': '128'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'servo.calendarevent': {
            'Meta': {'object_name': 'CalendarEvent'},
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Calendar']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'finished_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 14, 0, 0)'})
        },
        'servo.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'servo.contactinfo': {
            'Meta': {'object_name': 'ContactInfo'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'servo.customer': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Customer'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['servo.Device']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_company': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u'Uusi asiakas'", 'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'contacts'", 'null': 'True', 'to': "orm['servo.Customer']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'street_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['servo.Tag']", 'null': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        },
        'servo.device': {
            'Meta': {'object_name': 'Device'},
            'description': ('django.db.models.fields.CharField', [], {'default': "u'Uusi laite'", 'max_length': '128'}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Attachment']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'purchased_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['servo.Tag']", 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        },
        'servo.event': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'Event'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'handled_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ref': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'ref_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'triggered_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 14, 0, 0)'}),
            'triggered_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'servo.gsxaccount': {
            'Meta': {'object_name': 'GsxAccount'},
            'environment': ('django.db.models.fields.CharField', [], {'default': "('pr', u'Tuotanto')", 'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'ship_to': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sold_to': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Uusi tili'", 'max_length': '128'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'servo.inventory': {
            'Meta': {'object_name': 'Inventory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Product']"}),
            'slot': ('django.db.models.fields.IntegerField', [], {}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'})
        },
        'servo.invoice': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'Invoice'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 14, 0, 0)'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Customer']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'customer_address': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'customer_email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'customer_name': ('django.db.models.fields.CharField', [], {'default': "u'K\\xe4teisasiakas'", 'max_length': '128'}),
            'customer_phone': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Order']"}),
            'paid_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'payment_method': ('django.db.models.fields.IntegerField', [], {'default': "(0, u'Ei veloitusta')"}),
            'total_gross': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'total_margin': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'total_net': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'total_tax': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'servo.invoiceitem': {
            'Meta': {'object_name': 'InvoiceItem'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Invoice']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Product']"}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'servo.label': {
            'Meta': {'object_name': 'Label'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'servo.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'office_hours': ('django.db.models.fields.CharField', [], {'default': "'9:00 - 18:00'", 'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'ship_to': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Uusi toimipaikka'", 'max_length': '255'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        'servo.note': {
            'Meta': {'object_name': 'Note'},
            'attachments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['servo.Attachment']", 'null': 'True', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'code': ('django.db.models.fields.CharField', [], {'default': "'N5BJ46H'", 'max_length': '8'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 14, 0, 0)'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'flags': ('django.db.models.fields.CharField', [], {'default': "'01'", 'max_length': '2', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "('note', u'Merkint\\xe4')", 'max_length': '10'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Order']", 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'replies'", 'null': 'True', 'to': "orm['servo.Note']"}),
            'recipient': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'should_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'servo.notification': {
            'Meta': {'object_name': 'Notification'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        'servo.order': {
            'Meta': {'ordering': "['-priority', 'id']", 'object_name': 'Order'},
            'closed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 14, 0, 0)'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_by'", 'to': "orm['auth.User']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Customer']", 'null': 'True'}),
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['servo.Device']", 'null': 'True', 'blank': 'True'}),
            'followed_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'followed_by'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Location']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Product']", 'through': "orm['servo.ServiceOrderItem']", 'symmetrical': 'False'}),
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Queue']", 'null': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '16'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.QueueStatus']", 'null': 'True'}),
            'status_limit_green': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'status_limit_yellow': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Tag']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'servo.place': {
            'Meta': {'object_name': 'Place'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'servo.product': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Product'},
            'amount_minimum': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'amount_ordered': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'amount_reserved': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'amount_stocked': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'brand': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'component_code': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['servo.Attachment']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_serialized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pct_margin': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '4', 'decimal_places': '2'}),
            'pct_vat': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '4', 'decimal_places': '2'}),
            'price_exchange': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'price_notax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'price_purchase': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'price_sales': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'shelf': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '8', 'blank': 'True'}),
            'shipping': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['servo.Tag']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Uusi tuote'", 'max_length': '255'}),
            'warranty_period': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'servo.property': {
            'Meta': {'object_name': 'Property'},
            'format': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Uusi kentt\\xe4'", 'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "('customer', u'Asiakas')", 'max_length': '32'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'servo.purchaseorder': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'PurchaseOrder'},
            'carrier': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'confirmation': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 14, 0, 0)'}),
            'date_submitted': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'days_delivered': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'has_arrived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'sales_order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Order']", 'null': 'True', 'blank': 'True'}),
            'supplier': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'tracking_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'servo.purchaseorderitem': {
            'Meta': {'object_name': 'PurchaseOrderItem'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'date_ordered': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_received': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.ServiceOrderItem']", 'null': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Product']"}),
            'purchase_order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.PurchaseOrder']"}),
            'received_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'servo.queue': {
            'Meta': {'ordering': "['title']", 'object_name': 'Queue'},
            'default_status': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'default_status'", 'null': 'True', 'to': "orm['servo.Status']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dispatch_template': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'gsx_account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.GsxAccount']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_template': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'receipt_template': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'statuses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['servo.Status']", 'through': "orm['servo.QueueStatus']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Uusi jono'", 'unique': 'True', 'max_length': '255'})
        },
        'servo.queuestatus': {
            'Meta': {'object_name': 'QueueStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idx': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'limit_factor': ('django.db.models.fields.IntegerField', [], {'default': "(60, u'Minuuttia')"}),
            'limit_green': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'limit_yellow': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
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
        'servo.serviceorderitem': {
            'Meta': {'object_name': 'ServiceOrderItem'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dispatched': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Order']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'price_category': ('django.db.models.fields.CharField', [], {'default': "('warranty', u'Takuu')", 'max_length': '32'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Product']"}),
            'should_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'should_return': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'servo.status': {
            'Meta': {'object_name': 'Status'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_factor': ('django.db.models.fields.IntegerField', [], {'default': "(60, u'Minuuttia')"}),
            'limit_green': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'limit_yellow': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Uusi status'", 'unique': 'True', 'max_length': '255'})
        },
        'servo.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['servo.Tag']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'times_used': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Uusi tagi'", 'unique': 'True', 'max_length': '255'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'servo.template': {
            'Meta': {'object_name': 'Template'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Uusi pohja'", 'max_length': '128'})
        },
        'servo.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['servo.Location']", 'null': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'queues': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['servo.Queue']", 'null': 'True', 'blank': 'True'}),
            'tech_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['servo']