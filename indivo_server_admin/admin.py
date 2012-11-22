from django.contrib import admin
from django.core import urlresolvers
from django import forms

from indivo_server.indivo.models import *

DEVELOPMENT_MODE = True
#-------------------------------------------------------------------------
class AccountAdmin(admin.ModelAdmin):
    """
        This is the account (i.e. login). I would like to use this to 
        link to other related fields.
    """
    
    fields = (
        'full_name',
        'contact_email',
        'last_login_at',
        'last_failed_login_at',
        'total_login_count',
        'failed_login_count')

    if DEVELOPMENT_MODE:
        fields = ('primary_secret', 'secondary_secret') + fields

    list_display = ('full_name', 'contact_email', 'state')
    search_fields = ('full_name', 'contact_email')

admin.site.register(Account, AccountAdmin)
#-------------------------------------------------------------------------
class RecordAdmin(admin.ModelAdmin):
    list_display = ('label', 'external_id')
    search_fields = ('label',)
    readonly_fields = 'show_demographics_url', 'id'
    exclude='demographics',

    def show_demographics_url(self, obj):
        demographics_url = urlresolvers.reverse('admin:indivo_demographics_change', args=(obj.demographics.id,))
        return '<a href="%s">%s</a>' % (demographics_url, obj.demographics.name_given)

    show_demographics_url.allow_tags = True
    show_demographics_url.short_description = 'Demographics'

admin.site.register(Record, RecordAdmin)
#-------------------------------------------------------------------------
class DemographicsAdmin(admin.ModelAdmin):
    list_display = ('name_given', 'name_middle', 'name_family', 'bday', 'adr_city', 'tel_2_number')
    search_fields = ('name_family', 'name_given',  'name_middle')
    exclude='document',
    readonly_fields = 'document_url',

    def document_url(self, obj):
        document_url = urlresolvers.reverse('admin:indivo_document_change', args=(obj.document.id,))
        return '<a href="%s">%s : %s</a>' % (document_url, obj.document.fqn, obj.document.id)

    document_url.allow_tags = True
    document_url.short_description = 'Document'

admin.site.register(Demographics, DemographicsAdmin)

#-------------------------------------------------------------------------

class StatusField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
          return obj.name

class DocumentAdminForm(forms.ModelForm):
    status = StatusField(queryset=StatusName.objects.all()) 
    class Meta:
          model = Document

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'fqn', 'status_name')
    form = DocumentAdminForm

    def status_name(self, obj):
        return obj.status.name
    status_name.short_description = 'Status'
admin.site.register(Document, DocumentAdmin)
#-------------------------------------------------------------------------
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
admin.site.register(StatusName, StatusAdmin)
#-------------------------------------------------------------------------
class DocumentSchemaAdmin(admin.ModelAdmin):
    list_display = ('type', 'id')
    readonly_fields = 'id',
admin.site.register(DocumentSchema, DocumentSchemaAdmin)
#-------------------------------------------------------------------------
# This is configured via a django management command. Prevent editing via admin.
class PHAAdmin(admin.ModelAdmin):
    list_display = ('description', 'type', 'email', 'author')
    readonly_fields = ('id', 'creator', 'email', 'type', 'consumer_key', 'secret', 'name', 'description', 'author',
            'version', 'indivo_version', 'callback_url', 'start_url_template', 'is_autonomous', 'autonomous_reason',
            'has_ui', 'frameable', 'icon_url', 'requirements')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(PHA, PHAAdmin)
#--[ non-customised models ]----------------------------------------------
admin.site.register(AccessToken)
admin.site.register(AccountAuthSystem)
admin.site.register(AccountFullShare)
admin.site.register(Audit)
admin.site.register(Allergy)
admin.site.register(AllergyExclusion)
admin.site.register(AuthSystem)
admin.site.register(Carenet)
admin.site.register(CarenetAccount)
admin.site.register(CarenetAutoshare)
admin.site.register(CarenetDocument)
admin.site.register(CarenetPHA)
admin.site.register(DocumentRels)
admin.site.register(DocumentStatusHistory)
admin.site.register(Encounter)
admin.site.register(Equipment)
admin.site.register(Fact)
admin.site.register(Fill)
admin.site.register(Immunization)
admin.site.register(LabResult)
admin.site.register(MachineApp)
admin.site.register(Measurement)
admin.site.register(Medication)
admin.site.register(Message)
admin.site.register(MessageAttachment)
admin.site.register(Nonce)
admin.site.register(Notification)
admin.site.register(NoUser)
admin.site.register(PHAShare)
admin.site.register(Principal)
admin.site.register(Problem)
admin.site.register(Procedure)
admin.site.register(RecordNotificationRoute)
admin.site.register(ReqToken)
admin.site.register(SessionRequestToken)
admin.site.register(SessionToken)
admin.site.register(SimpleClinicalNote)
admin.site.register(VitalSigns)
