VAULT   := vault
DATASET := dataset
SCRIPT  := scripts/frontmatter_to_csv.py

SUBVAULTS := module person faculty level reading-list book paper

.PHONY: all clean

all: $(addprefix $(DATASET)/,$(addsuffix .csv,$(SUBVAULTS)))

$(DATASET):
	mkdir -p $@

define csv_rule
$(DATASET)/$(1).csv: $(wildcard $(VAULT)/$(1)/*.md) $(SCRIPT) | $(DATASET)
	python3 $(SCRIPT) $(VAULT)/$(1) > $$@
endef

$(foreach sv,$(SUBVAULTS),$(eval $(call csv_rule,$(sv))))

clean:
	rm -rf $(DATASET)
