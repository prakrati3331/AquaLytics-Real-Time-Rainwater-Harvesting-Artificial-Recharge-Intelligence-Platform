import pandas as pd
from file_handling import parseDepth

class RainwaterHarvesting:
    def __init__(self, roofArea, roofType, rainfallMM, dwellers, dailyDemand=7):
        self.roofArea = roofArea
        self.roofType = roofType
        self.rainfallMM = rainfallMM
        self.dwellers = dwellers
        self.dailyDemand = dailyDemand
        self.runoffCoeff = {
            "CONCRETE": 0.85,
            "GI_SHEET": 0.80,
            "TILE": 0.75,
            "THATCHED": 0.60
        }

    def annualDemand(self):
        return self.dwellers * self.dailyDemand * 365

    def harvestedWaterFromRoof(self):
        coeff = self.runoffCoeff.get(self.roofType.upper(), 0.0)
        return self.rainfallMM * self.roofArea * coeff

    def rainfallFactor(self):
        return min(self.rainfallMM / 1000, 1)

    def runoffFactor(self):
        harvestedWater = self.harvestedWaterFromRoof()
        return min(harvestedWater / (self.roofArea * 600), 1)

    def feasibility(self, groundwaterPre, groundwaterPost, aquiferScore):
        if self.rainfallMM < 350:
            return -1

        remark = ""
        if groundwaterPre == 'N.A.':
            remark = 'Missing PreMonsoon groundwater Data, using assumptions...'
            groundwaterPre = '10'
        if groundwaterPost == 'N.A.':
            remark = 'Missing PostMonsoon groundwater Data, using assumptions...'
            groundwaterPost = '10'
        if groundwaterPost == '2':
            remark = 'No real need for as groundwater is available at just 2 mbgl'

        groundwaterLevel = max(
            0, 
            (parseDepth(groundwaterPre) - parseDepth(groundwaterPost)) / parseDepth(groundwaterPre)
        )

        aquiferFactor = aquiferScore / 5

        feasibility = (
            0.3 * self.rainfallFactor() +
            0.25 * self.runoffFactor() +
            0.25 * groundwaterLevel +
            0.2 * aquiferFactor
        )

        return feasibility
