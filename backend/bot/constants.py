from backend.util.position_adapter import PositionLike

class PathConstants:
    ConfigFile = "config.json"

class PositionalConstants:
    DeveloperResolution = (2560, 1440)

    class Schema:
        Counts = 5
        ButtonInterval = 100
        RecentButton = (261, 690-(Counts-1)*ButtonInterval)
        
        @staticmethod
        def Button(index: int):
            """
            0: recently used schema
            1...: custom schemas
            """
            if index < 0 or index >= PositionalConstants.Schema.Counts:
                raise ValueError("Invalid schema button index")
            x, y = PositionalConstants.Schema.RecentButton
            y += index * PositionalConstants.Schema.ButtonInterval
            return x, y


    PurchaseButton = (2257, 1154)
    
    PriceRangeTopLeft = (2200, 1150)
    PriceRangeBottomRight = (2330, 1175)
    
    WarningRangeTopLeft = (1233, 989)
    WarningRangeBottomRight = (1360, 1020)

    @staticmethod
    def get_mapped(coord: PositionLike, resolution: PositionLike = None):
        if resolution is None:
            resolution = PositionalConstants.DeveloperResolution
        maxX, maxY = resolution
        x, y = coord
        x_ratio = maxX / PositionalConstants.DeveloperResolution[0]
        y_ratio = maxY / PositionalConstants.DeveloperResolution[1]
        return (int(x * x_ratio), int(y * y_ratio))
    
    @staticmethod
    def to_ratio(range: PositionLike):
        x, y = range
        X, Y = PositionalConstants.DeveloperResolution
        return x/X, y/Y
    
    @staticmethod
    def to_ratio_range(coord1: PositionLike, coord2: PositionLike):
        x1, y1 = PositionalConstants.to_ratio(coord1)
        x2, y2 = PositionalConstants.to_ratio(coord2)
        return (x1, y1, x2, y2)
