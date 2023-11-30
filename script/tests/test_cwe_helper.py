from .. import cwe_helper


class TestCWEHelperClass:
    cwe_data = None

    @classmethod
    def setup_class(self):
        self.cwe_data = cwe_helper.load_cwe_taxonomy()

    def test_load_cwe_data(self):
        assert type(self.cwe_data) == dict

    def test_get_top_categories(self):
        top_40 = cwe_helper._get_top_cwe_699_categories(cwe_data=self.cwe_data)
        assert len(top_40.items()) == 40

        top_pillars = cwe_helper._get_top_cwe_1000_pillars(
            cwe_data=self.cwe_data
        )
        assert len(top_pillars.items()) == 10

    # direct children
    def test_get_relevant_cwe_699(self):
        # 699
        behavioral_cwe = cwe_helper.get_relevant_cwe699_category(
            cwe_data=self.cwe_data, cwes=["115"]
        )

        assert len(behavioral_cwe) == 1
        assert behavioral_cwe[0] == "438"

        behavioral_cwe = cwe_helper.get_relevant_cwe699_category(
            cwe_data=self.cwe_data, cwes=["115", "484"]
        )

        assert len(behavioral_cwe) == 1
        assert behavioral_cwe[0] == "438"

    def test_get_relevant_cwe_1000(self):
        target_cwe = cwe_helper.get_relevant_cwe1000_pillar(
            cwe_data=self.cwe_data, cwes=["20"]
        )

        assert len(target_cwe) == 1
        assert target_cwe[0] == "707"

        target_cwe = cwe_helper.get_relevant_cwe1000_pillar(
            cwe_data=self.cwe_data, cwes=["20", "172"]
        )

        assert len(target_cwe) == 1
        assert target_cwe[0] == "707"

    # direct children, multiple categories
    def test_get_mulitple_relevant_cwes_699(self):
        mixed_cwes = cwe_helper.get_relevant_cwe699_category(
            cwe_data=self.cwe_data, cwes=["331"]
        )
        assert len(mixed_cwes) == 2
        assert sorted(mixed_cwes) == sorted(["1213", "310"])

    # direct children, multiple categories
    def test_get_mulitple_relevant_cwes_1000(self):
        # inapplicable
        # mixed_cwes = cwe_helper.get_relevant_cwe1000_pillar(
        #     cwe_data=self.cwe_data, cwes=["188"]
        # )
        # assert len(mixed_cwes) == 2
        # assert sorted(mixed_cwes) == sorted(["435", "710"])
        pass

    # partial miss / hit
    def test_partial_miss_relevant_cwes_699(self):
        partial_missed_cwes = cwe_helper.get_relevant_cwe699_category(
            cwe_data=self.cwe_data, cwes=["9999999", "115"]
        )
        assert len(partial_missed_cwes) == 1
        assert partial_missed_cwes == ["438"]

        partial_missed_cwes = cwe_helper.get_relevant_cwe699_category(
            cwe_data=self.cwe_data, cwes=["9999999", "331"]
        )
        assert len(partial_missed_cwes) == 2
        assert sorted(partial_missed_cwes) == sorted(["1213", "310"])

    # partial miss / hit
    def test_partial_miss_relevant_cwes_1000(self):
        partial_missed_cwes = cwe_helper.get_relevant_cwe1000_pillar(
            cwe_data=self.cwe_data, cwes=["9999999", "20"]
        )
        assert len(partial_missed_cwes) == 1
        assert partial_missed_cwes == ["707"]

        partial_missed_cwes = cwe_helper.get_relevant_cwe1000_pillar(
            cwe_data=self.cwe_data, cwes=["9999999", "234"]
        )
        assert len(partial_missed_cwes) == 2
        assert sorted(partial_missed_cwes) == sorted(["703", "707"])

    # miss
    def test_miss_relevant_cwes_699(self):
        missed_cwes = cwe_helper.get_relevant_cwe699_category(
            cwe_data=self.cwe_data, cwes=["9999999"]
        )
        assert len(missed_cwes) == 1
        assert missed_cwes == ["-1"]

    # miss
    def test_miss_relevant_cwes_1000(self):
        missed_cwes = cwe_helper.get_relevant_cwe1000_pillar(
            cwe_data=self.cwe_data, cwes=["9999999"]
        )
        assert len(missed_cwes) == 1
        assert missed_cwes == ["-1"]

    # trace cwe tree function
    def test_trace_weaknesses_function_699(self):
        cwe_699_categories = cwe_helper._get_top_cwe_699_categories(
            cwe_data=self.cwe_data
        )
        traced_cwes = cwe_helper._trace_related_weaknesses(
            cwe_data=self.cwe_data,
            top_category_dict=cwe_699_categories,
            subject_cwe="457",
        )
        assert len(traced_cwes) == 1
        assert traced_cwes == ["399"]

    # trace cwe tree function
    def test_trace_weaknesses_function_1000(self):
        pass

    # tree traversal
    def test_direct_relevant_cwes_699(self):
        # single
        grand_child_cwes = cwe_helper.get_relevant_cwe699_category(
            cwe_data=self.cwe_data, cwes=["457"]
        )
        assert len(grand_child_cwes) == 1
        assert grand_child_cwes == ["399"]

        # multiple
        grand_child_cwes = cwe_helper.get_relevant_cwe699_category(
            cwe_data=self.cwe_data, cwes=["226"]
        )

        assert len(grand_child_cwes) == 2
        assert sorted(grand_child_cwes) == sorted(["199", "452"])

    def test_direct_relevant_cwes_1000(self):
        pass

    def test_distance_upward_relevant_cwes_699(self):
        # not found
        grand_child_cwes = cwe_helper.get_relevant_cwe699_category(
            cwe_data=self.cwe_data, cwes=["666"]
        )
        assert len(grand_child_cwes) == 1
        assert grand_child_cwes == ["-1"]

        # single
        # [699] <- ww <- xx <- yy <- zz
        grand_child_cwes = cwe_helper.get_relevant_cwe699_category(
            cwe_data=self.cwe_data, cwes=["24"]
        )
        assert len(grand_child_cwes) == 1
        assert grand_child_cwes == ["1219"]

        # multiple
        grand_child_cwes = cwe_helper.get_relevant_cwe699_category(
            cwe_data=self.cwe_data, cwes=["590"]
        )

        assert len(grand_child_cwes) == 2
        assert sorted(grand_child_cwes) == sorted(["399", "465"])

    def test_distance_upward_relevant_cwes_1000(self):
        # not found
        grand_child_cwes = cwe_helper.get_relevant_cwe1000_pillar(
            cwe_data=self.cwe_data, cwes=["699"]
        )
        assert len(grand_child_cwes) == 1
        assert grand_child_cwes == ["-1"]

        # single
        # [1000] <- ww <- xx <- yy <- zz
        grand_child_cwes = cwe_helper.get_relevant_cwe1000_pillar(
            cwe_data=self.cwe_data, cwes=["175"]
        )
        assert len(grand_child_cwes) == 1
        assert grand_child_cwes == ["707"]

        # multiple
        grand_child_cwes = cwe_helper.get_relevant_cwe1000_pillar(
            cwe_data=self.cwe_data, cwes=["234"]
        )

        assert len(grand_child_cwes) == 2
        assert sorted(grand_child_cwes) == sorted(["703", "707"])

    def test_suspecious_mapping(self):
        grand_child_cwes = cwe_helper.get_relevant_cwe1000_pillar(
            cwe_data=self.cwe_data, cwes=["415"]
        )
        assert len(grand_child_cwes) == 2
        assert sorted(grand_child_cwes) == sorted(["664", "710"])
