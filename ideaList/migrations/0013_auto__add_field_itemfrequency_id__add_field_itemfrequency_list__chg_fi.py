# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        #NOTE: added the id column manually:
        # ALTER TABLE "ideaList_itemfrequency" ADD COLUMN "id" INTEGER;
        # CREATE SEQUENCE "ideaList_itemfrequency_id_seq";
        # UPDATE "ideaList_itemfrequency" SET id = nextval('"ideaList_itemfrequency_id_seq"');
        # ALTER TABLE "ideaList_itemfrequency"
        # ALTER COLUMN "id" SET DEFAULT nextval('"ideaList_itemfrequency_id_seq"');
        # ALTER TABLE "ideaList_itemfrequency"
        # ALTER COLUMN "id" SET NOT NULL;
        # ALTER TABLE "ideaList_itemfrequency" ADD UNIQUE ("id");
        # ALTER TABLE "ideaList_itemfrequency" DROP CONSTRAINT "ideaList_itemfrequency_id_key" RESTRICT;
        # ALTER TABLE "ideaList_itemfrequency" ADD PRIMARY KEY ("id");

        # Removing unique constraint on 'ItemFrequency', fields ['text']
        db.delete_unique('ideaList_itemfrequency', ['text'])

        # Changing field 'ItemFrequency.text'
        db.alter_column('ideaList_itemfrequency', 'text', self.gf('django.db.models.fields.CharField')(max_length=200))

        # Adding field 'ItemFrequency.id'
        db.add_column('ideaList_itemfrequency', 'id', self.gf('django.db.models.fields.AutoField')(default=1, primary_key=True), keep_default=False)

        # Adding field 'ItemFrequency.list'
        db.add_column('ideaList_itemfrequency', 'list', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='itemfrequencies', to=orm['ideaList.List']), keep_default=False)
        # Adding unique constraint on 'ItemFrequency', fields ['text', 'list']
        db.create_unique('ideaList_itemfrequency', ['text', 'list_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ItemFrequency', fields ['text', 'list']
        db.delete_unique('ideaList_itemfrequency', ['text', 'list_id'])

        # Deleting field 'ItemFrequency.id'
        db.delete_column('ideaList_itemfrequency', 'id')

        # Deleting field 'ItemFrequency.list'
        db.delete_column('ideaList_itemfrequency', 'list_id')

        # Changing field 'ItemFrequency.text'
        db.alter_column('ideaList_itemfrequency', 'text', self.gf('django.db.models.fields.CharField')(max_length=200, primary_key=True))

        # Adding unique constraint on 'ItemFrequency', fields ['text']
        db.create_unique('ideaList_itemfrequency', ['text'])


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
        'ideaList.item': {
            'Meta': {'ordering': "['position']", 'object_name': 'Item'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'important': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['ideaList.List']"}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'trashed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'ideaList.itemfrequency': {
            'Meta': {'ordering': "['-frequency']", 'unique_together': "(('list', 'text'),)", 'object_name': 'ItemFrequency'},
            'frequency': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'itemfrequencies'", 'to': "orm['ideaList.List']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'ideaList.list': {
            'Meta': {'object_name': 'List'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lists_owned'", 'to': "orm['auth.User']"}),
            'subscribers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'subscribed_lists'", 'symmetrical': 'False', 'through': "orm['ideaList.Subscription']", 'to': "orm['auth.User']"}),
            'trashed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'ideaList.subscription': {
            'Meta': {'ordering': "['position']", 'unique_together': "(('user', 'list'),)", 'object_name': 'Subscription'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': "orm['ideaList.List']"}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'trashed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['ideaList']
