from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Domain(models.Model):
    """EarthRISE domains/fields of expertise"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Prompt(models.Model):
    """Expert prompts shared by EarthRISE users"""
    VISIBILITY_CHOICES = [
        ('public', 'Public - All EarthRISE users'),
        ('domain', 'Domain - Only domain members'),
        ('private', 'Private - Only me'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Brief description of what this prompt does")
    model_used = models.TextField(help_text="What model(s) this prompt is designed for (e.g. GPT-4, Gemini Pro, etc.)", blank=True)
    prompt_text = models.TextField(help_text="The actual prompt text")
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='prompts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompts')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    upvotes = models.ManyToManyField(User, related_name='upvoted_prompts', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_prompts', blank=True)

    slug = models.SlugField(unique=True, blank=True, max_length=250)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['domain', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Prompt.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('prompt_detail', kwargs={'slug': self.slug})

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def get_upvote_count(self):
        """Get the count of upvotes"""
        return self.upvotes.count()

    def get_favorite_count(self):
        """Get the count of favorites"""
        return self.favorites.count()

    def get_comment_count(self):
        """Get the count of comments"""
        return self.comments.count()


class Comment(models.Model):
    """Comments on prompts"""
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.prompt.title}"


class AllowedEmail(models.Model):
    """Email addresses that are automatically added to EarthRISE group on first login"""
    email = models.EmailField(unique=True, db_index=True)
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='allowed_emails_added'
    )
    notes = models.TextField(blank=True, help_text="Optional notes about this email/user")

    class Meta:
        ordering = ['email']
        verbose_name = 'Allowed Email'
        verbose_name_plural = 'Allowed Emails'

    def __str__(self):
        return self.email