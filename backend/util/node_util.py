class NodeType:
    BLOODPOINTS = "bloodpoints"
    PRESTIGE = "prestige"
    ORIGIN = "origin"
    ORIGIN_AUTO_ENABLED = "origin_auto_enabled"
    ORIGIN_AUTO_DISABLED = "origin_auto_disabled"
    CLAIMED = "claimed"
    ACCESSIBLE = "accessible"
    INACCESSIBLE = "inaccessible"
    STOLEN = "stolen"
    VOID = "void"

    MULTI_UNCLAIMED = [ACCESSIBLE, INACCESSIBLE]
    MULTI_ORIGIN_AUTO = [ORIGIN_AUTO_ENABLED, ORIGIN_AUTO_DISABLED]
    MULTI_CLAIMABLE = [ACCESSIBLE, INACCESSIBLE, PRESTIGE, ORIGIN_AUTO_ENABLED, ORIGIN_AUTO_DISABLED]

class ColorUtil:
    red_hex = "#C80A0A"
    red_rgb = (200, 10, 10)

    taupe_hex = "#969664"
    taupe_rgb = (150, 150, 100)

    neutral_hex = "#37323C"
    neutral_rgb = (55, 50, 60)

    black_hex = "#000000"
    black_rgb = (0, 0, 0)

    @staticmethod
    def hex_from_cls_name(cls_name):
        return ColorUtil.red_hex if cls_name in [NodeType.BLOODPOINTS, NodeType.PRESTIGE, NodeType.ORIGIN,
                                                 NodeType.ORIGIN_AUTO_ENABLED, NodeType.ORIGIN_AUTO_DISABLED,
                                                 NodeType.CLAIMED] else \
            ColorUtil.taupe_hex if cls_name == NodeType.ACCESSIBLE else \
            ColorUtil.neutral_hex if cls_name == NodeType.INACCESSIBLE else \
            ColorUtil.black_hex

    @staticmethod
    def rgb_from_cls_name(cls_name):
        return ColorUtil.red_rgb if cls_name in [NodeType.BLOODPOINTS, NodeType.PRESTIGE, NodeType.ORIGIN,
                                                 NodeType.ORIGIN_AUTO_ENABLED, NodeType.ORIGIN_AUTO_DISABLED,
                                                 NodeType.CLAIMED] else \
            ColorUtil.taupe_rgb if cls_name == NodeType.ACCESSIBLE else \
            ColorUtil.neutral_rgb if cls_name == NodeType.INACCESSIBLE else \
            ColorUtil.black_rgb

    @staticmethod
    def bgr_from_cls_name(cls_name):
        return tuple(reversed(ColorUtil.rgb_from_cls_name(cls_name)))