import urllib
import os, os.path

from django.contrib import admin
from django.core import urlresolvers
from django import forms
from django.utils.html import escape

from admin_enhancer.admin import EnhancedModelAdminMixin

from indivo_server.indivo import models as indivo_models
from indivo_server.codingsystems import models as coding_models

from settings import CORE_SCHEMA_DIRS, CONTRIB_SCHEMA_DIRS

DEVELOPMENT_MODE = True

# This puts links on foreignkey fields
class DefaultModelAdmin(EnhancedModelAdminMixin, admin.ModelAdmin):
    pass

class RecordField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s (%s)" % (obj.label, obj.id)

class StatusField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
          return obj.name

class SystemField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.short_name
#-------------------------------------------------------------------------
class AccountAdmin(DefaultModelAdmin):
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
        # TODO: if supervisor
        fields = ('primary_secret', 'secondary_secret') + fields

    list_display = ('full_name', 'contact_email', 'state')
    search_fields = ('full_name', 'contact_email')

    def get_form(self, request, obj=None, **kwargs):
        form = super(AccountAdmin, self).get_form(request, obj, **kwargs)
        form.sidebar_name = "Links"
        sidebar = []
        record_url = urlresolvers.reverse('admin:indivo_record_changelist')
        sidebar += ['<a href="%s?owner__id__exact=%s">Records</a>' % (record_url, obj.id)]
        carenet_url = urlresolvers.reverse('admin:indivo_carenetaccount_changelist')
        sidebar += ['<a href="%s?account=%s">Carenets</a>' % (carenet_url, obj.id)]
        form.sidebar = "<br/>".join(sidebar)
        return form

admin.site.register(indivo_models.Account, AccountAdmin)
#-------------------------------------------------------------------------
class RecordAdmin(DefaultModelAdmin):
    list_display = ('label', 'external_id', 'owner')
    search_fields = ('label',)
    readonly_fields = 'show_demographics_url', 'id'
    exclude='demographics',

    def show_demographics_url(self, obj):
        demographics_url = urlresolvers.reverse('admin:indivo_demographics_change', args=(obj.demographics.id,))
        return '<a href="%s">%s</a>' % (demographics_url, obj.demographics.name_given)

    show_demographics_url.allow_tags = True
    show_demographics_url.short_description = 'Demographics'

    def get_form(self, request, obj=None, **kwargs):
        form = super(RecordAdmin, self).get_form(request, obj, **kwargs)
        form.sidebar_name = "Links"
        sidebar = []
        account_url = urlresolvers.reverse('admin:indivo_account_change', args=(obj.owner.id,))
        sidebar += ['<a href="%s">Account</a>' % account_url]
        demographics_url = urlresolvers.reverse('admin:indivo_demographics_change', args=(obj.demographics.id,))
        sidebar += ['<a href="%s">Demographics</a>' % demographics_url]
        carenet_url = urlresolvers.reverse('admin:indivo_carenet_changelist')
        sidebar += ['<a href="%s?record__id__exact=%s">Carenets</a>' % (carenet_url, obj.id)]
        document_url = urlresolvers.reverse('admin:indivo_document_changelist')
        sidebar += ['<a href="%s?record__id__exact=%s">Documents</a>' % (document_url, obj.id)]
        sidebar += ["<h3>Facts</h3>"]
        allergy_url = urlresolvers.reverse('admin:indivo_allergy_changelist')
        sidebar += ['<a href="%s?record__id__exact=%s">Allergys</a>' % (allergy_url, obj.id)]
        immunization_url = urlresolvers.reverse('admin:indivo_immunization_changelist')
        sidebar += ['<a href="%s?record__id__exact=%s">Immunizations</a>' % (immunization_url, obj.id)]
        labresult_url = urlresolvers.reverse('admin:indivo_labresult_changelist')
        sidebar += ['<a href="%s?record__id__exact=%s">Lab Results</a>' % (labresult_url, obj.id)]
        measurement_url = urlresolvers.reverse('admin:indivo_measurement_changelist')
        sidebar += ['<a href="%s?record__id__exact=%s">Measurements</a>' % (measurement_url, obj.id)]
        medication_url = urlresolvers.reverse('admin:indivo_medication_changelist')
        sidebar += ['<a href="%s?record__id__exact=%s">Medications</a>' % (medication_url, obj.id)]
        procedure_url = urlresolvers.reverse('admin:indivo_procedure_changelist')
        sidebar += ['<a href="%s?record__id__exact=%s">Procedures</a>' % (procedure_url, obj.id)]
        simpleclinicalnote_url = urlresolvers.reverse('admin:indivo_simpleclinicalnote_changelist')
        sidebar += ['<a href="%s?record__id__exact=%s">Simple Clinical Notes</a>' % (simpleclinicalnote_url, obj.id)]
        vitalsigns_url = urlresolvers.reverse('admin:indivo_vitalsigns_changelist')
        sidebar += ['<a href="%s?record__id__exact=%s">Vital Signs</a>' % (vitalsigns_url, obj.id)]
        form.sidebar = "<br/>".join(sidebar)
        return form

admin.site.register(indivo_models.Record, RecordAdmin)
#-------------------------------------------------------------------------
class DemographicsAdmin(DefaultModelAdmin):
    list_display = ('name_given', 'name_middle', 'name_family', 'bday', 'adr_city', 'tel_2_number')
    search_fields = ('name_family', 'name_given',  'name_middle')
    exclude='document',
    readonly_fields = 'document_url',

    def document_url(self, obj):
        document_url = urlresolvers.reverse('admin:indivo_document_change', args=(obj.document.id,))
        return '<a href="%s">%s : %s</a>' % (document_url, obj.document.fqn, obj.document.id)

    document_url.allow_tags = True
    document_url.short_description = 'Document'

    def get_form(self, request, obj=None, **kwargs):
        form = super(DemographicsAdmin, self).get_form(request, obj, **kwargs)
        form.sidebar_name = "Links"
        sidebar = []
        record_url = urlresolvers.reverse('admin:indivo_record_change', args=(obj.record.id,))
        sidebar += ['<a href="%s">Record</a>' % record_url]
        form.sidebar = "<br/>".join(sidebar)
        return form

admin.site.register(indivo_models.Demographics, DemographicsAdmin)

#-------------------------------------------------------------------------

class DocumentAdminForm(forms.ModelForm):
    status = StatusField(queryset=indivo_models.StatusName.objects.all()) 
    record = RecordField(queryset=indivo_models.Record.objects.all()) 
    class Meta:
          model = indivo_models.Document

class DocumentAdmin(DefaultModelAdmin):
    list_display = ('id', 'fqn', 'status_name', 'record', 'created_at', 'suppressed_at')
    readonly_fields = 'id',
    form = DocumentAdminForm

    def status_name(self, obj):
        return obj.status.name
    status_name.short_description = 'Status'

    def get_form(self, request, obj=None, **kwargs):
        form = super(DocumentAdmin, self).get_form(request, obj, **kwargs)
        form.sidebar_name = "Links"
        sidebar = []
        record_url = urlresolvers.reverse('admin:indivo_record_change', args=(obj.record.id,))
        sidebar += ['<a href="%s">Record</a>' % record_url]
        account_url = urlresolvers.reverse('admin:indivo_account_change', args=(obj.record.owner.id,))
        sidebar += ['<a href="%s">Account</a>' % account_url]
        facts_url = urlresolvers.reverse('admin:indivo_fact_changelist')
        sidebar += ['<a href="%s?document=%s">Facts</a>' % (facts_url, obj.id)]
        schema_url = urlresolvers.reverse('admin:indivo_documentschema_changelist')
        sidebar += ['<a href="%s?type=%s">Schema</a>' % (schema_url, urllib.quote(obj.fqn))]
        form.sidebar = "<br/>".join(sidebar)
        return form

admin.site.register(indivo_models.Document, DocumentAdmin)
#-------------------------------------------------------------------------
class DocumentStatusAdminForm(forms.ModelForm):
    status = StatusField(queryset=indivo_models.StatusName.objects.all()) 
    class Meta:
          model = indivo_models.DocumentStatusHistory
class DocumentStatusModelAdmin(DefaultModelAdmin):
    form = DocumentStatusAdminForm
admin.site.register(indivo_models.DocumentStatusHistory, DocumentStatusModelAdmin)
#-------------------------------------------------------------------------
class StatusAdmin(DefaultModelAdmin):
    list_display = ('name', 'id')
admin.site.register(indivo_models.StatusName, StatusAdmin)
#-------------------------------------------------------------------------
class DocumentSchemaAdmin(DefaultModelAdmin):
    list_display = ('type', 'id', 'stylesheet')
    readonly_fields = 'id', 'schemafile', 'transformfile'

    def schemafile(self, obj):
        # I have to read the schema file directly, as it may be invalid
        # and not visible via the document_processing api
        # Unfortunately, the directory name cannot be relied on. simpleclinicalnote
        # is in the folder simple note. I am not parsing the documents, so I might
        # be picking up text in another document
        filename = obj.type.split("#")[1]
        for root in CONTRIB_SCHEMA_DIRS + CORE_SCHEMA_DIRS:
            for dirname in [d for d in os.listdir(root) if os.path.exists(root+os.sep+d+os.sep+"schema.xsd")]:
                fullpath = root + os.sep + dirname + os.sep + "schema.xsd"
                document = open(fullpath).read()
                if document.find(filename) == -1:
                    continue
                return "<b>%s</b><pre><br/>" % fullpath + escape(document) + "</pre>"
        return "SCHEMA NO FOUND IN %s" % (CONTRIB_SCHEMA_DIRS+CORE_SCHEMA_DIRS)
    schemafile.allow_tags = True
    schemafile.short_description = 'Schema (XSD)'

    def transformfile(self, obj):
        # I have to read the schema file directly, as it may be invalid
        # and not visible via the document_processing api
        filename = obj.type.split("#")[1]
        for root in CONTRIB_SCHEMA_DIRS + CORE_SCHEMA_DIRS:
            for dirname in [d for d in os.listdir(root) if os.path.exists(root+os.sep+d+os.sep+"transform.xsl")]:
                fullpath = root + os.sep + dirname + os.sep + "transform.xsl"
                document = open(fullpath).read()
                if document.find(filename) == -1:
                    continue
                return "<b>%s</b><pre><br/>" % fullpath + escape(document) + "</pre>"
        return "SCHEMA TRANSFORM FOUND IN %s" % (CONTRIB_SCHEMA_DIRS+CORE_SCHEMA_DIRS)
    transformfile.allow_tags = True
    transformfile.short_description = 'Transform (XSL)'

    def get_form(self, request, obj=None, **kwargs):
        form = super(DocumentSchemaAdmin, self).get_form(request, obj, **kwargs)
        form.sidebar_name = "Links"
        sidebar = []
        document_url = urlresolvers.reverse('admin:indivo_document_changelist')
        sidebar += ['<a href="%s?fqn=%s">Documents</a>' % (document_url, urllib.quote(obj.type))]
        form.sidebar = "<br/>".join(sidebar)
        return form

admin.site.register(indivo_models.DocumentSchema, DocumentSchemaAdmin)
#-------------------------------------------------------------------------
# This is configured via a django management command. Prevent editing via admin.
class PHAAdmin(DefaultModelAdmin):
    list_display = ('description', 'type', 'email', 'author')
    readonly_fields = ('id', 'creator', 'email', 'type', 'consumer_key', 'secret', 'name', 'description', 'author',
            'version', 'indivo_version', 'callback_url', 'start_url_template', 'is_autonomous', 'autonomous_reason',
            'has_ui', 'frameable', 'icon_url', 'requirements')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(indivo_models.PHA, PHAAdmin)
#-------------------------------------------------------------------------
class AuditAdmin(DefaultModelAdmin):
    list_display = ('view_func', 'pha_id', 'datetime', 'effective_principal_email', 'record_id', 'document_id')
    list_filter = ('view_func', 'pha_id', 'record_id')
    exclude = ('record_id', 'document_id')

    readonly_fields = ('record_id_url', 'document_id_url',
        'datetime', 'view_func', 'request_successful', 'effective_principal_email', 'proxied_by_email',
        'carenet_id', 'pha_id', 'external_id', 'message_id', 'req_url', 'req_ip_address',
        'req_domain', 'req_headers', 'req_method', 'resp_code', 'resp_headers',)

    def record_id_url(self, obj):
        if obj.record_id:
            url = urlresolvers.reverse('admin:indivo_record_change', args=(obj.record_id,))
            return '<a href="%s">%s</a>' % (url, obj.record_id)
        else:
            "no record"
    record_id_url.allow_tags = True
    record_id_url.short_description = 'Record'

    def document_id_url(self, obj):
        if obj.document_id:
            url = urlresolvers.reverse('admin:indivo_document_change', args=(obj.document_id,))
            return '<a href="%s">%s</a>' % (url, obj.document_id)
        else:
            return "no document"
    document_id_url.allow_tags = True
    document_id_url.short_description = 'Document'
    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(indivo_models.Audit, AuditAdmin)

#-------------------------------------------------------------------------
class EncounterAdmin(DefaultModelAdmin):
    list_display = ('startDate', 'endDate', 'facility_name', 'get_provider_name', 'encounterType_title')
    list_filter = ('facility_name', 'encounterType_title')
    exclude = ('id',)
    readonly_fields = 'fact_url',
    def get_provider_name(self, obj):
        parts = [field for field in [ obj.provider_name_prefix, obj.provider_name_given,
                obj.provider_name_middle, obj.provider_name_family, obj.provider_name_suffix] if field]
        return ''.join(parts)
    get_provider_name.short_description = 'Provider'

    def fact_url(self, obj):
        if obj.id:
            url = urlresolvers.reverse('admin:indivo_fact_change', args=(obj.id,))
            return '<a href="%s">Fact: %s</a>' % (url, obj.id)
        else:
            return "no record"
    fact_url.allow_tags = True
    fact_url.short_description = 'Fact'

admin.site.register(indivo_models.Encounter, EncounterAdmin)
#-------------------------------------------------------------------------

class FactAdminForm(forms.ModelForm):
    record = RecordField(queryset=indivo_models.Record.objects.all()) 
    class Meta:
          model = coding_models.CodedValue

class FactAdmin(DefaultModelAdmin):
    readonly_fields = 'id','created_at'
    list_display = ('created_at', 'get_document_name', 'get_record_name')
    def get_record_name(self, obj):
        return obj.record.label
    get_record_name.short_description = 'Record'
    def get_document_name(self, obj):
        return '%s (%s)' % (obj.document.fqn, obj.document.id)
    get_document_name.short_description = 'Document'
    form = FactAdminForm

admin.site.register(indivo_models.Fact, FactAdmin)
#-------------------------------------------------------------------------
class CarenetModelAdmin(DefaultModelAdmin):
    list_display = ('id', 'name', 'record')

    def get_form(self, request, obj=None, **kwargs):
        form = super(CarenetModelAdmin, self).get_form(request, obj, **kwargs)
        form.sidebar_name = "Links"
        sidebar = []
        record_url = urlresolvers.reverse('admin:indivo_record_change', args=(obj.record.id,))
        sidebar += ['<a href="%s">Record</a>' % record_url]
        carenet_url = urlresolvers.reverse('admin:indivo_carenet_changelist')
        sidebar += ['<a href="%s?record__id__exact=%s">Sibling Carenets</a>' % (carenet_url, obj.record.id)]
        carenet_accounts_url = urlresolvers.reverse('admin:indivo_carenetaccount_changelist')
        sidebar += ['<a href="%s?carenet__id__exact=%s">Subscribed Accounts</a>' % (carenet_accounts_url, obj.id)]
        form.sidebar = "<br/>".join(sidebar)
        return form

admin.site.register(indivo_models.Carenet, CarenetModelAdmin)
#-------------------------------------------------------------------------
class CarenetAccountModelAdmin(DefaultModelAdmin):
    list_display = ('id', 'carenet', 'account')

    def get_form(self, request, obj=None, **kwargs):
        form = super(CarenetAccountModelAdmin, self).get_form(request, obj, **kwargs)
        form.sidebar_name = "Links"
        sidebar = []
        carenet_url = urlresolvers.reverse('admin:indivo_carenet_change', args=(obj.carenet.id,))
        sidebar += ['<a href="%s">Carenet</a>' % carenet_url]
        account_url = urlresolvers.reverse('admin:indivo_account_change', args=(obj.account.id,))
        sidebar += ['<a href="%s">Account</a>' % account_url]
        form.sidebar = "<br/>".join(sidebar)
        return form

admin.site.register(indivo_models.CarenetAccount, CarenetAccountModelAdmin)

#--[ non-customised FACT models ]----------------------------------------------
class AllergyModelAdmin(DefaultModelAdmin):
    list_display = ('id', 'record', 'category_title')
admin.site.register(indivo_models.Allergy, AllergyModelAdmin)
admin.site.register(indivo_models.AllergyExclusion, DefaultModelAdmin)
admin.site.register(indivo_models.Fill, DefaultModelAdmin)
admin.site.register(indivo_models.Immunization, DefaultModelAdmin)
admin.site.register(indivo_models.LabResult, DefaultModelAdmin)
admin.site.register(indivo_models.Measurement, DefaultModelAdmin)
admin.site.register(indivo_models.Medication, DefaultModelAdmin)
admin.site.register(indivo_models.Problem, DefaultModelAdmin)
admin.site.register(indivo_models.Procedure, DefaultModelAdmin)
admin.site.register(indivo_models.SimpleClinicalNote, DefaultModelAdmin)
admin.site.register(indivo_models.VitalSigns, DefaultModelAdmin)

#--[ non-customised models ]----------------------------------------------
admin.site.register(indivo_models.AccountAuthSystem, DefaultModelAdmin)
admin.site.register(indivo_models.AccountFullShare, DefaultModelAdmin)
admin.site.register(indivo_models.AuthSystem, DefaultModelAdmin)
admin.site.register(indivo_models.CarenetAutoshare, DefaultModelAdmin)
admin.site.register(indivo_models.CarenetDocument, DefaultModelAdmin)
admin.site.register(indivo_models.CarenetPHA, DefaultModelAdmin)
admin.site.register(indivo_models.DocumentRels, DefaultModelAdmin)
admin.site.register(indivo_models.Equipment, DefaultModelAdmin)
admin.site.register(indivo_models.MachineApp, DefaultModelAdmin)
admin.site.register(indivo_models.Message, DefaultModelAdmin)
admin.site.register(indivo_models.MessageAttachment, DefaultModelAdmin)
admin.site.register(indivo_models.Notification, DefaultModelAdmin)
admin.site.register(indivo_models.NoUser, DefaultModelAdmin)
admin.site.register(indivo_models.PHAShare, DefaultModelAdmin)
admin.site.register(indivo_models.Principal, DefaultModelAdmin)
admin.site.register(indivo_models.RecordNotificationRoute, DefaultModelAdmin)

#--------[ Session Stuff ]--------------------------------------
admin.site.register(indivo_models.AccessToken, DefaultModelAdmin)
admin.site.register(indivo_models.Nonce, DefaultModelAdmin)
admin.site.register(indivo_models.ReqToken, DefaultModelAdmin)
admin.site.register(indivo_models.SessionRequestToken, DefaultModelAdmin)
admin.site.register(indivo_models.SessionToken, DefaultModelAdmin)
#--------[ Coding Systems ]--------------------------------------

class CodingSystemAdmin(DefaultModelAdmin):
    list_display = ('short_name', 'description')
admin.site.register(coding_models.CodingSystem, CodingSystemAdmin)

class CodedValueAdminForm(forms.ModelForm):
    system = SystemField(queryset=coding_models.CodingSystem.objects.all()) 
    class Meta:
          model = coding_models.CodedValue

class CodedValueAdmin(DefaultModelAdmin):
    def get_system_name(self, obj):
        return obj.system.short_name
    get_system_name.short_description = 'System'
    list_display = ('get_system_name', 'code', 'physician_value', 'consumer_value', 'umls_code')
    search_fields = ('code', 'abbreviation', 'physician_value', 'consumer_value', 'umls_code')
    list_filter = ('system__short_name',)
    form = CodedValueAdminForm
admin.site.register(coding_models.CodedValue, CodedValueAdmin)

