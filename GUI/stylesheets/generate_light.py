import json


#TODO: need to do this before writing paper
colordict = {
      "WindowBackground" : "#efefef",
      "AlternateWindowBackground":"#e3e3e3",
      "WindowText": "#3c3c77",
      "Base" : "#ffffff",
      "TooltipBase" : "#ffffdc",
      "TooltipText" : "#3c3c77",
      "ButtonBackground" : "#eeeef6",
      "ButtonText" : "#3c3c77",
      "Link" : "#2A82DA",
      "Highlight" : "#D9B36D",
      "HighlightDark" : "#B2842E",
      "HighlightedText" : "#3c3c77",
      "AlternateBaseBackground" : "#d9d9d9",
      "Text" : "#3c3c77",
      "BrightText" : "#FF0000",
      "DisabledWindow" : "#eeeef6",
      "DisabledWindowText" : "#3c3c77",
      "DisabledBase" : "#d9d9d9",
      "DisabledAlternateBase" : "#eeeef6",
      "DisabledTooltip" : "#3c3c77",
      "DisabledTooltipText" : "#3c3c77",
      "DisabledText" : "#3c3c77",
      "DisabledButton" : "#eeeef6",
      "DisabledButtonText" : "#eeeef6",
      "DisabledBrightText" : "#FF0000",
      "DisabledLink" : "#2A82DA",
      "DisabledHighlight" : "#2A82DA",
      "DisabledHighlightText" : "#3c3c77",
      'plotBg': "#d9d9d9",
      'plot_db': '#003359',
      'plot_mb': '#0076a9',
      'plot_lb': '#001219', #AE2012
      'plot_b': '#0066cc',
      'plot_t': '#005F73', #
      'plot_p': '#0A9396', #
      'plot_la': '#94D2BD', #
      'plot_g': '#AE2012', #
      'plot_c': '#822433',
      'plot_r': '#EE9B00', #
      'plot_ro': '#f23f00',
      'plot_o': '#CA6702', #
      'plot_a': '#BB3E03', #
      'plot_y': '#AE2012', #
      'plot_gr': '#999999',
      'plot_wgr': '#82786f',
      'plot_bgr': '#7d8ea0' }

with open('light_colors.json', 'w') as fp:
    json.dump(colordict, fp, sort_keys=True, indent=4)