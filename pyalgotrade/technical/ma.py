# PyAlgoTrade
# 
# Copyright 2011 Gabriel Martin Becedillas Ruiz
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

from pyalgotrade import technical

def calculate_sma(filterDS, firstPos, lastPos):
	accum = 0
	for i in xrange(firstPos, lastPos+1):
		value = filterDS.getValueAbsolute(i)
		if value is None:
			return None
		accum += value

	ret = accum / float(lastPos - firstPos + 1)
	return ret

# This is the formula I'm using to calculate the averages based on previous ones.
# 1 2 3 4
# x x x
#   x x x
# 
# avg0 = (a + b + c) / 3
# avg1 = (b + c + d) / 3 
# 
# avg0 = avg1 + x
# (a + b + c) / 3 = (b + c + d) / 3 + x
# a/3 + b/3 + c/3 = b/3 + c/3 + d/3 + x
# a/3 = d/3 + x
# x = a/3 - d/3

# avg1 = avg0 - x 
# avg1 = avg0 + d/3 - a/3

class SMA(technical.DataSeriesFilter):
	"""Simple Moving Average filter.

	:param dataSeries: The DataSeries instance being filtered.
	:type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
	:param period: The number of values to use to calculate the SMA.
	:type period: int.
	"""

	def __init__(self, dataSeries, period):
		technical.DataSeriesFilter.__init__(self, dataSeries, period)
		self.__prevAvg = None
		self.__prevAvgPos = None

	def __calculateFastSMA(self, firstPos, lastPos):
		assert(firstPos > 0)
		firstValue = self.getDataSeries().getValueAbsolute(firstPos-1)
		lastValue = self.getDataSeries().getValueAbsolute(lastPos)
		if lastValue is None:
			return None

		self.__prevAvg = self.__prevAvg + lastValue / float(self.getPeriod()) - firstValue / float(self.getPeriod())
		self.__prevAvgPos = lastPos
		return self.__prevAvg

	def __calculateSMA(self, firstPos, lastPos):
		ret = calculate_sma(self.getDataSeries(), firstPos, lastPos)
		self.__prevAvg = ret
		self.__prevAvgPos = lastPos
		return ret

	def getPeriod(self):
		return self.getWindowSize()

	def calculateValue(self, firstPos, lastPos):
		if self.__prevAvgPos != None and self.__prevAvgPos == lastPos - 1:
			ret = self.__calculateFastSMA(firstPos, lastPos)
		else:
			ret = self.__calculateSMA(firstPos, lastPos)
		return ret

class EMA(technical.DataSeriesFilter):
	"""Exponential Moving Average filter.

	:param dataSeries: The DataSeries instance being filtered.
	:type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
	:param period: The number of values to use to calculate the EMA.
	:type period: int.
	"""

	def __init__(self, dataSeries, period):
		technical.DataSeriesFilter.__init__(self, dataSeries, period)

	def getPeriod(self):
		return self.getWindowSize()

	def calculateValue(self, firstPos, lastPos):
		# Formula from http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_averages
		if lastPos == self.getFirstValidPos():
			# First average is a SMA.
			ret = calculate_sma(self.getDataSeries(), firstPos, lastPos)
		else:
			currValue = self.getDataSeries().getValueAbsolute(lastPos)
			prevEMA = self.getValueAbsolute(lastPos - 1)
			multiplier = (2.0 / (self.getPeriod() + 1))
			ret = (currValue - prevEMA) * multiplier + prevEMA
		return ret

class WMA(technical.DataSeriesFilter):
	"""Weighted Moving Average filter.

	:param dataSeries: The DataSeries instance being filtered.
	:type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
	:param weights: A list of int/float with the weights.
	:type weights: list.
	
	"""
	def __init__(self, dataSeries, weights):
		technical.DataSeriesFilter.__init__(self, dataSeries, len(weights))
		self.__weights = weights

	def getPeriod(self):
		return self.getWindowSize()

	def getWeights(self):
		return self.__weights

	def calculateValue(self, firstPos, lastPos):
		accum = 0
		weightSum = 0
		for i in xrange(firstPos, lastPos+1):
			value = self.getDataSeries().getValueAbsolute(i)
			if value is None:
				return None

			weight = self.__weights[i - firstPos]
			accum += value * weight
			weightSum += weight
		return accum / float(weightSum)

