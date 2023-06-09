import json



colordict = {
      "WindowBackground" : "#16162b",
      "AlternateWindowBackground":"#1b1b36",
      "WindowText": "#FFFFFF",
      "Base" : "#0d0d1a",
      "TooltipBase" : "#28284d",
      "TooltipText" : "#FFFFFF",
      "ButtonBackground" : "#1b1b36",
      "ButtonText" : "#FFFFFF",
      "Link" : "#2A82DA",
      "Highlight" : "#d0a149",
      "HighlightDark" : "#8e6925",
      "HighlightedText" : "#FFFFFF",
      "AlternateBaseBackground" : "#28284d",
      "Text" : "#FFFFFF",
      "BrightText" : "#FF0000",
      "DisabledWindow" : "#1b1b36",
      "DisabledWindowText" : "#696969",
      "DisabledBase" : "#1b1b36",
      "DisabledAlternateBase" : "#1b1b36",
      "DisabledTooltip" : "#FFFFFF",
      "DisabledTooltipText" : "#FFFFFF",
      "DisabledText" : "#696969",
      "DisabledButton" : "#1b1b36",
      "DisabledButtonText" : "#696969",
      "DisabledBrightText" : "#FF0000",
      "DisabledLink" : "#2A82DA",
      "DisabledHighlight" : "#2A82DA",
      "DisabledHighlightText" : "#000000",
      'plotBg': "#28284d",
      'plot_db': '#003359',
      'plot_mb': '#0076a9',
      'plot_lb': '#264653', #
      'plot_b': '#0066cc',
      'plot_t': '#2a9d8f', #
      'plot_p': '#e9c46a', #
      'plot_la': '#f4a261', #
      'plot_g': '#e76f51', #
      'plot_c': '#822433',
      'plot_r': '#d496a7', #
      'plot_ro': '#f23f00',
      'plot_o': '#9d695a', #
      'plot_a': '#26547C', #
      'plot_y': '#ffd166', #
      'plot_gr': '#999999',
      'plot_wgr': '#82786f',
      'plot_bgr': '#7d8ea0'}



with open('dark_colors.json', 'w') as fp:
    json.dump(colordict, fp, sort_keys=True, indent=4)