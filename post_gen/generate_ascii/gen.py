from .ascii_art import (
    goLang, divider_xl, performance_mode, divider_l, tools, divider_s,
    gRPC, divider_mono, protoC, autoMaxProcs, ants, zeroLog,
    goFast, gRpc_ProtoBuf, server, by, wjb_dev, go,
)
from .frame import TextFramer

def print_go_performance_mode_art():

    logo = TextFramer(border_char_x="", border_char_y="", padding=0, align="left")
    print(logo.frame([go]))
    
    go_performance_mode = [
        goLang, divider_xl, performance_mode, divider_l, tools, divider_s,
        gRPC, divider_mono, protoC, divider_mono, autoMaxProcs, divider_mono,
        ants, divider_mono, zeroLog,
    ]
    
    fancy = TextFramer(border_char_x="=", border_char_y="||", padding=2, align="left")
    print(fancy.frame(go_performance_mode))

    go_fast = [
        goFast, gRpc_ProtoBuf, server,
        by, wjb_dev
    ]
    footer = TextFramer(border_char_x="", border_char_y="", padding=2, align="left")
    print(footer.frame(go_fast))
