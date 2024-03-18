from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page


class Group(Page, ClusterableModel):
    parent_page_types = ["wagtailcore.Page"]


class Module(Page, ClusterableModel):
    parent = ParentalKey(
        Group,
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name=Group._meta.verbose_name,
    )

    parent_page_types = ["content.Group"]
    content_panels = [
        TitleFieldPanel("title", classname="full title"),
    ]

    def save(self, **kwargs):
        self.parent = self.get_parent().specific
        super().save(**kwargs)

    @cached_property
    def index(self):
        return self.parent.modules.filter(path__lte=self.path).count()

    def get_admin_display_title(self):
        return f"{self.index}. {self.title}"


class Screen(Page):

    TYPES = (
        ("intro", _("Intro")),
        ("read", _("Read")),
    )

    module_parent = ParentalKey(
        Module,
        on_delete=models.CASCADE,
        related_name="screens",
        verbose_name=Module._meta.verbose_name,
    )

    type = models.CharField(choices=TYPES, max_length=256)
    extra = models.BooleanField(default=False)

    content = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title")),
            ("paragraph", blocks.RichTextBlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    parent_page_types = ["content.Module"]

    content_panels = [
        TitleFieldPanel("title", classname="full title"),
        FieldPanel("type",
                   help_text=_("What function does this screen serve?")),
        FieldPanel("extra", help_text=_("Is this screen optional?")),
        FieldPanel("content"),
    ]

    def save(self, *args, **kwargs):
        self.module_parent = self.get_parent().specific
        super().save(*args, **kwargs)

    @cached_property
    def index(self):
        return self.module_parent.screens.filter(path__lte=self.path).count()

    def get_admin_display_title(self):
        return f"{self.index}. {self.title}"
