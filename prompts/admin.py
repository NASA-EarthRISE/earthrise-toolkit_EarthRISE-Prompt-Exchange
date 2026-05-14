from django.contrib import admin
from django.db.models import Count
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Domain, Prompt, Comment, AllowedEmail


class AllowedEmailResource(resources.ModelResource):
    class Meta:
        model = AllowedEmail
        fields = ('id', 'email', 'notes', 'added_at')
        import_id_fields = ('email',)
        skip_unchanged = True


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'prompt_count']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def prompt_count(self, obj):
        return obj.prompts.count()

    prompt_count.short_description = 'Number of Prompts'


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'model_used', 'domain', 'visibility', 'display_upvote_count', 'created_at']
    list_filter = ['visibility', 'domain', 'created_at', 'model_used']
    search_fields = ['title', 'description', 'prompt_text', 'tags', 'model_used']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'slug', 'display_upvote_count', 'display_favorite_count',
                       'display_comment_count']
    filter_horizontal = ['upvotes', 'favorites']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'domain')
        }),
        ('Content', {
            'fields': ('description', 'model_used', 'prompt_text', 'tags')
        }),
        ('Settings', {
            'fields': ('visibility',)
        }),
        ('Engagement', {
            'fields': ('upvotes', 'favorites', 'display_upvote_count', 'display_favorite_count',
                       'display_comment_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_upvote_count(self, obj):
        if hasattr(obj, 'upvotes_count'):
            return obj.upvotes_count
        return obj.upvotes.count()

    display_upvote_count.short_description = 'Upvotes'
    display_upvote_count.admin_order_field = 'upvotes_count'

    def display_favorite_count(self, obj):
        if hasattr(obj, 'favorites_count'):
            return obj.favorites_count
        return obj.favorites.count()

    display_favorite_count.short_description = 'Favorites'

    def display_comment_count(self, obj):
        if hasattr(obj, 'comments_count'):
            return obj.comments_count
        return obj.comments.count()

    display_comment_count.short_description = 'Comments'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('author', 'domain').annotate(
            upvotes_count=Count('upvotes', distinct=True),
            favorites_count=Count('favorites', distinct=True),
            comments_count=Count('comments', distinct=True)
        )
        return qs


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'author', 'text_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'author__username', 'prompt__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_preview.short_description = 'Comment Preview'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author', 'prompt')


@admin.register(AllowedEmail)
class AllowedEmailAdmin(ImportExportModelAdmin):
    resource_class = AllowedEmailResource
    list_display = ['email', 'added_at', 'added_by']
    search_fields = ['email', 'notes']
    list_filter = ['added_at']
    readonly_fields = ['added_at']

    def save_model(self, request, obj, form, change):
        """Automatically set added_by to current user if not set"""
        if not change:  # Only on creation
            obj.added_by = request.user
        super().save_model(request, obj, form, change)

# Customize admin site headers
admin.site.site_header = "EarthRISE Prompt Exchange Administration"
admin.site.site_title = "EarthRISE Prompt Exchange Admin"
admin.site.index_title = "Welcome to EarthRISE Prompt Exchange Administration"