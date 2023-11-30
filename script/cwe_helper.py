from xml.dom.minidom import parseString, Element


# retrieve cwe dictionary from the downloaded dictionary
# https://cwe.mitre.org/data/xml/cwec_latest.xml.zip
# current version 4.12 (2023-07)
def load_cwe_taxonomy() -> dict:
    cwe_xml = open("../data-ref/cwe-dictionary/cwec_v4.12.xml", "r")
    result = cwe_xml.read()
    cwe_xml.close()

    cwe = parseString(result)

    categories = cwe.getElementsByTagName("Category")
    weaknesses = cwe.getElementsByTagName("Weakness")

    return {"categories": categories, "weaknesses": weaknesses}


# get list of cwes under categories in 699
def _get_top_cwe_699_categories(cwe_data: dict) -> dict:
    categories = cwe_data["categories"]

    cwe_699_categories = {}
    category: Element
    for category in categories:
        category_id = category.getAttribute("ID")

        members = category.getElementsByTagName("Has_Member")

        for member in members:
            view_id = member.getAttribute("View_ID")
            member_cwe_id = member.getAttribute("CWE_ID")

            if str(view_id) == "699":
                if category_id not in cwe_699_categories.keys():
                    cwe_699_categories[category_id] = []

                cwe_699_categories[category_id].append(member_cwe_id)

    return cwe_699_categories


# get list of cwes under pillars in 1000
def _get_top_cwe_1000_pillars(cwe_data: dict) -> dict:
    weaknesses = cwe_data["weaknesses"]
    cwe_1000_pillars = {}

    # first pass - define pillars
    weakness: Element
    for weakness in weaknesses:
        if weakness.getAttribute("Abstraction") == "Pillar":
            pillar_id = weakness.getAttribute("ID")
            if pillar_id not in cwe_1000_pillars.keys():
                cwe_1000_pillars[pillar_id] = []

    # second pass - collect top level weaknesses
    weakness: Element
    for weakness in weaknesses:
        weakness_id = weakness.getAttribute("ID")
        related_weaknesses = weakness.getElementsByTagName("Related_Weakness")

        for related_weakness in related_weaknesses:
            related_weakness_id = related_weakness.getAttribute("CWE_ID")
            related_weakness_nature = related_weakness.getAttribute("Nature")

            if (
                str(related_weakness_id) in cwe_1000_pillars.keys()
                and related_weakness_nature == "ChildOf"
            ):
                cwe_1000_pillars[related_weakness_id].append(weakness_id)

    return cwe_1000_pillars


def _trace_related_weaknesses(
    cwe_data: dict,
    top_category_dict: dict,
    subject_cwe: str,
    # match any related peer weaknesses - first round only
    accept_side_relation: bool = True,
    consider_pillar: bool = False,
):
    # print("trace for cwe: ", subject_cwe)
    weaknesses = cwe_data["weaknesses"]
    cwe_categories = []

    weakness: Element
    for weakness in weaknesses:
        weakness_id = weakness.getAttribute("ID")
        weakness_abstraction = weakness.getAttribute("Abstraction")

        # found subject weakness - check related weaknesses
        if str(subject_cwe) == str(weakness_id):
            # exit if the subject weekness is Pillar - already at the top of tree
            if weakness_abstraction == "Pillar":
                if consider_pillar:
                    return [weakness_id]
                return []

            related_weaknesses = weakness.getElementsByTagName("Related_Weakness")

            # round 1: one-level relation
            parent_cwes = []
            for related_weakness in related_weaknesses:
                nature = related_weakness.getAttribute("Nature")
                related_weakness_cwe_id = related_weakness.getAttribute("CWE_ID")
                related_weakness_view_id = related_weakness.getAttribute("View_ID")
                # print("related weakness ", related_weakness_cwe_id)
                cwe_categories += [
                    str(k)
                    for k, v in top_category_dict.items()
                    if str(related_weakness_cwe_id) in v and (accept_side_relation)
                ]
                # print(cwe_categories)

                # only use parent-child because other relations turn tree to graph
                # Pan et al. https://baolingfeng.github.io/papers/ICSE2023.pdf

                # only continue if data do not meet outdate criteria
                if nature == "ChildOf" and related_weakness_view_id == "1000":
                    parent_cwes.append(related_weakness_cwe_id)

            parent_cwes = list(set(parent_cwes))
            # round 2: more than one level - upward only - recursive
            if len(cwe_categories) == 0:
                # search if parent cwes are related to any 699 categories
                for parent_cwe in parent_cwes:
                    cwe_categories += _trace_related_weaknesses(
                        cwe_data=cwe_data,
                        top_category_dict=top_category_dict,
                        subject_cwe=parent_cwe,
                        accept_side_relation=accept_side_relation,
                        consider_pillar=consider_pillar,
                    )

    return cwe_categories


def get_relevant_cwe_groups(
    cwe_data: dict,
    target_groups: dict,
    cwes: list,
    accept_side_relation: bool = True,
    consider_pillar: bool = False,
) -> list:
    # print(target_groups)
    hit_cwes = []
    # remove a cwe when hit
    already_hit_cwes = []
    for k, v in target_groups.items():
        for cwe in cwes:
            if str(cwe) in v or str(cwe) == k:
                hit_cwes.append(k)
                already_hit_cwes.append(cwe)

    cwes = [cwe for cwe in cwes if cwe not in already_hit_cwes]

    # if there's cwe left, try tracing tree
    if len(cwes) > 0:
        for cwe in cwes:
            hit_cwes += _trace_related_weaknesses(
                cwe_data=cwe_data,
                top_category_dict=target_groups,
                accept_side_relation=accept_side_relation,
                subject_cwe=cwe,
                consider_pillar=consider_pillar,
            )

    # final catch, if given cwes cannot be mapped to 699
    # return undefined category ["-1"] for flagging
    if len(hit_cwes) == 0:
        return ["-1"]

    return list(set(hit_cwes))


# given a list of CWEs, return the closet category(s) from CWE-699
def get_relevant_cwe699_category(cwe_data: dict, cwes: list) -> list:
    cwe_699_categories = _get_top_cwe_699_categories(cwe_data=cwe_data)

    return list(
        set(
            get_relevant_cwe_groups(
                cwe_data=cwe_data, target_groups=cwe_699_categories, cwes=cwes
            )
        )
    )


# given a list of CWEs, return the closet pillar(s) from CWE-1000
def get_relevant_cwe1000_pillar(cwe_data: dict, cwes: list) -> list:
    cwe_1000_pillars = _get_top_cwe_1000_pillars(cwe_data=cwe_data)

    return list(
        set(
            get_relevant_cwe_groups(
                cwe_data=cwe_data,
                target_groups=cwe_1000_pillars,
                cwes=cwes,
                accept_side_relation=False,
                consider_pillar=True,
            )
        )
    )
