from functools import partial

import graphene
from django.conf import settings
from graphene_django import DjangoObjectType
from graphene_django.types import ALL_FIELDS
from parler.models import TranslatableModel


def _parler_field_resolver(attname, instance, info, language=None):
    if language:
        return instance.safe_translation_getter(attname, language_code=language)

    return getattr(instance, attname)

def _get_language_choices_from_parler_settings():
    site_id = getattr(settings, "SITE_ID", None)
    parler_languages = settings.PARLER_LANGUAGES.get(site_id, [])

    choices = []
    for parler_language in parler_languages:
        language_code = parler_language["code"]
        choices.append((language_code.upper(), language_code))

    return choices

TranslationLanguage = graphene.Enum(
    "TranslationLanguage", _get_language_choices_from_parler_settings()
)

class DjangoParlerObjectType(DjangoObjectType):
    class Meta:
        abstract = True

    @classmethod
    def _add_parler_fields_to_type(cls, model, fields=None, exclude=None):
        """Adds fields in the model that are translated with Parler to the Object Type

        If the class defines an attribute with the same name already, the attribute is
        left as is and the translated field is not added to the class.
        """
        for parler_field_name in model._parler_meta.get_all_fields():
            if (
                hasattr(cls, parler_field_name)
                or (
                    fields is not None
                    and fields != ALL_FIELDS
                    and parler_field_name not in fields
                )
                or (exclude is not None and parler_field_name in exclude)
            ):
                continue

            setattr(
                cls,
                parler_field_name,
                graphene.String(
                    language=graphene.String(),#TranslationLanguage(),
                    resolver=partial(_parler_field_resolver, parler_field_name),
                ),
            )

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        model=None,
        registry=None,
        skip_registry=False,
        only_fields=None,
        fields=None,
        exclude_fields=None,
        exclude=None,
        filter_fields=None,
        filterset_class=None,
        connection=None,
        connection_class=None,
        use_connection=None,
        interfaces=(),
        convert_choices_to_enum=True,
        _meta=None,
        **options
    ):
        assert issubclass(model, TranslatableModel), (
            'You need to pass a valid Django Parler Model in {}.Meta, received "{}".'
        ).format(cls.__name__, model)

        # Notice: only_fields and exclude_fields are deprecated and are not used here
        cls._add_parler_fields_to_type(model, fields, exclude)

        super().__init_subclass_with_meta__(
            model=model,
            registry=registry,
            skip_registry=skip_registry,
            only_fields=only_fields,
            fields=fields,
            exclude_fields=exclude_fields,
            exclude=exclude,
            filter_fields=filter_fields,
            filterset_class=filterset_class,
            connection=connection,
            connection_class=connection_class,
            use_connection=use_connection,
            interfaces=interfaces,
            convert_choices_to_enum=convert_choices_to_enum,
            _meta=_meta,
            **options
        )