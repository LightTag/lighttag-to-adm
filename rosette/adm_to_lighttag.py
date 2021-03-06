from typing import Callable, List

from rosette.type_definitions.adm_types import ADMDoc, Entity
from lighttag.type_definitions import LTSuggestionInput, LTExampleSuggestionsWithTestament, \
    LTSuggestionsWithTestaments
from configuration import ConfigurationUtil


config = ConfigurationUtil.get_configuration()

lt2adm_tags_names = config['LIGHTTAG2ADMMAPPING']['TAGS']
adm2lt_tags_names = dict()

for key, value in lt2adm_tags_names.items():
    adm2lt_tags_names[value] = key




def default_example_id_fn(doc: ADMDoc) -> str:
    # TODO @Nadav, I think you changed the type of the metadata to be a list ?
    return doc["documentMetadata"]["lighttag_example_id"][0]


def default_tag_name_extractor(entity: Entity) -> str:

    return entity["type"]


def resolved_tag_name_extractor(entity: Entity) -> str:

    if entity['type'] in adm2lt_tags_names.keys():
        return adm2lt_tags_names[entity['type']]
    else:
        return "ERROR"


    return entity["type"]


def adm_doc_to_lighttag_suggetions(
    doc: ADMDoc,
    example_id_fn: Callable[[ADMDoc], str] = default_example_id_fn,
    lighttag_tag_name_extractor: Callable[[Entity], str] = resolved_tag_name_extractor,
) -> LTExampleSuggestionsWithTestament:
    """

    :param doc:  An ADMDoc container the predictions from Rosette
    :param example_id_fn: A function that extracts the LightTag example_id from the adm doc
    :param lighttag_tag_name_extractor: A function that converts the entity type into the name of the tag in LightTag
    :return: LightTag suggestions to be sent to LightTag
    """
    example_id = example_id_fn(doc)
    predictied_entities = doc["attributes"]["entities"]["items"]
    suggestions: List[LTSuggestionInput] = []
    for adm_prediction in predictied_entities:
        tag = lighttag_tag_name_extractor(adm_prediction)
        if tag != 'ERROR':
            mention = adm_prediction["mentions"][0]
            suggestion: LTSuggestionInput = {
                "tag": tag,
                "example_id": example_id,
                "start": mention["startOffset"],
                "end": mention["endOffset"],
                "text": mention["normalized"],
            }
            suggestions.append(suggestion)
    return {
        'suggestions':suggestions,
        'seen_example_id':example_id
    }


def adm_document_list_to_lighttag_suggestions(
    docs: List[ADMDoc],
    example_id_fn: Callable[[ADMDoc], str] = default_example_id_fn,
    lighttag_tag_name_extractor: Callable[[Entity], str] = resolved_tag_name_extractor,
) ->LTSuggestionsWithTestaments:
    """

    :param docs: A list of ADM Docs
    :param example_id_fn:
    :param lighttag_tag_name_extractor:
    :return: LightTag suggestions to be sent to LightTag
    """
    result :LTSuggestionsWithTestaments = {
        'suggestions':[],
        'seen_example_ids':[]
    }

    for doc in docs:
        testament_with_suggestions :LTExampleSuggestionsWithTestament = adm_doc_to_lighttag_suggetions(
            doc,
            example_id_fn=example_id_fn,
            lighttag_tag_name_extractor=lighttag_tag_name_extractor,
        )
        result['suggestions']+=testament_with_suggestions['suggestions']
        result['seen_example_ids'].append(testament_with_suggestions['seen_example_id'])
    return result
