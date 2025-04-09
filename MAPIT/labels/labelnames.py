import json

# this short script consolidates the key labels that are associated with the MAPIT GUI
# arr1 contains the international labels
# arr2 contains the domestic (US) labels

intdictlab = {
      "OuterL" : "Analysis",
      "Box1L" : "Operations",
      "Box11L" : "Simulate measurement error",
      "Box12L" : "MUF",
      "Box13L" : "Active Inventory",
      "Box14L" : "Cumulative ID",
      "Box15L" : "Sigma MUF",
      "Box16L" : "Sigma MUF (Active Inventory)",
      "Box17L" : "SITMUF",
      "Box18L" : "Page's test on SITMUF",
      "Box2L" : "Statistics",
      "Box21L" : "MBP",
      "Box22L" : "Iterations",
      "Box23L" : "Analysis Elements/Index",
      "Box24L" : "Temporal Offset",
      "Box25L" : "Set Simulated Errors",
      "Box26L" : "Run",
      "Box3L" : "Plot Controls",
      "Box31L" : "Plot Data Type",
      "Box32L" : "Plot Data Location",
      "Box33L" : "",
      "Box33Lb" : "Contribution Type",
      "Box34L" : "Iterations to Plot",
      "Box4L" : "Statistical Thresholds",
      "Box41L" : "Enter Threshold",
      "Box42L" : "% Above Threshold:",
      "Box43L" : "Calculate",
      "Box44L" : "Random",
      "Box45L" : "Systematic",
      "Box46L" : "SEID Contribution (Absolute)",
      "Box47L" : "SEID Contribution (Relative)",
      "Box49L" : "Sigma MUF (AI) Contribution (Absolute)",
      "Box50L" : "Sigma MUF (AI) Contribution (Relative)",
      "Box51L": "GEMUF (V1)",
      "Box52L": "GEMUF (V5)",
      "Box48L": "Total"
    }

domdictlab = {
      "OuterL" : "Analysis",
      "Box1L" : "Operations",
      "Box11L" : "Simulate measurement error",
      "Box12L" : "ID",
      "Box13L" : "Active Inventory",
      "Box14L" : "CUMUF",
      "Box15L" : "SEID",
      "Box16L" : "SEID (Active Inventory)",
      "Box17L" : "SITMUF",
      "Box18L" : "Page's test on SITMUF",
      "Box2L" : "Statistics",
      "Box21L" : "MBP",
      "Box22L" : "Iterations",
      "Box23L" : "Analysis Elements/Index",
      "Box24L" : "Temporal Offset",
      "Box25L" : "Set Simulated Errors",
      "Box26L" : "Run",
      "Box3L" : "Plot Controls",
      "Box31L" : "Plot Data Type",
      "Box32L" : "Plot Data Location",
      "Box33L" : "",
      "Box33Lb" : "Contribution Type",
      "Box34L" : "Iterations to Plot",
      "Box4L" : "Statistical Thresholds",
      "Box41L" : "Enter Threshold",
      "Box42L" : "% Above Threshold:",
      "Box43L" : "Calculate",
      "Box44L" : "Random",
      "Box45L" : "Systematic",
      "Box46L" : "SEID Contribution (Absolute)",
      "Box47L" : "SEID Contribution (Relative)",
      "Box49L" : "SEID (AI) Contribution (Absolute)",
      "Box50L" : "SEID (AI) Contribution (Relative)",
      "Box51L": "GEMUF (V1)",
      "Box52L": "GEMUF (V5)",
      "Box48L": "Total "
    }

mdls = {1: "Fuel Fab"}
datasets = {1: "Normal",
            2: "Abrupt Loss",
            3: "Protract Loss"}

with open('intLabels.json', 'w') as fp:
    json.dump(intdictlab, fp, sort_keys=True, indent=4)

with open('domLabels.json', 'w') as fp:
    json.dump(domdictlab, fp, sort_keys=True, indent=4)

with open('exemplarMdls.json', 'w') as fp:
    json.dump(mdls, fp, sort_keys=True, indent=4)

with open('exemplarDatas.json', 'w') as fp:
    json.dump(datasets, fp, sort_keys=True, indent=4)