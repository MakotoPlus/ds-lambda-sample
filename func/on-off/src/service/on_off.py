import logging
import copy
import datetime
from abc import ABCMeta, abstractmethod

logger = logging.getLogger()


class OnOff(metaclass=ABCMeta):
  DICT_SWITCH_KEY = 'switch'
  DICT_CHECK_DATE_YYYYMMDD = 'check_date_yyyymmdd'
  SWITCH_ON = 'on'
  SWITCH_OFF = 'off'

  def __init__(self, name, event):
    self._name = name
    self.event = self._check_event_dict(event)
    self.event = self._set_date(self.event)

  @property
  def name(self):
    return self._name

  def _check_event_dict(self, event) -> dict:
    if not (OnOff.DICT_SWITCH_KEY in event ):
      raise Exception(f'{self.name} event parameter key is not key:{OnOff.DICT_SWITCH_KEY}')

    switch_value = event[OnOff.DICT_SWITCH_KEY]
    if OnOff.SWITCH_ON != switch_value and OnOff.SWITCH_OFF != switch_value:
      raise Exception(f'{self.name} event parameter value error {switch_value}')
    return event


  def _set_date(self, event) -> dict:
    # 日付設定
    result_dict = copy.deepcopy(event)
    check_date_yyyymmdd = datetime.date.today()
    if OnOff.DICT_CHECK_DATE_YYYYMMDD in result_dict :
      s_check_date_yyyymmdd = result_dict[OnOff.DICT_CHECK_DATE_YYYYMMDD]
      year = s_check_date_yyyymmdd[0:4]
      month = s_check_date_yyyymmdd[4:6]
      dd = s_check_date_yyyymmdd[6:8]
      print(f'{year}/{month}/{dd} {s_check_date_yyyymmdd}')
      check_date_yyyymmdd = datetime.date(int(year), int(month), int(dd))
    result_dict[OnOff.DICT_CHECK_DATE_YYYYMMDD] = check_date_yyyymmdd
    return result_dict


  def run(self):
    '''
    処理実行
    - SWITCH_ON:=平日時は実行メソッド _on()を呼出すが平日以外の場合は何もしないで終了する
    - SWITCH_OFF:=いつでも実行メソッド _off()を呼出す
    '''
    if self.event[OnOff.DICT_SWITCH_KEY] == OnOff.SWITCH_ON:
      logger.info(f"{self.name}起動 処理開始" \
        f"({self.event[OnOff.DICT_CHECK_DATE_YYYYMMDD].strftime('%Y/%m/%d')})")
      if self._is_running(self.event[OnOff.DICT_CHECK_DATE_YYYYMMDD]):
        self._on()
      logger.info(f"{self.name}起動 処理完了" \
        f"({self.event[OnOff.DICT_CHECK_DATE_YYYYMMDD].strftime('%Y/%m/%d')})")        
    else:
      logger.info(f"{self.name}停止 処理開始" \
        f"({self.event[OnOff.DICT_CHECK_DATE_YYYYMMDD].strftime('%Y/%m/%d')})")      
      self._off()
      logger.info(f"{self.name}停止 処理完了" \
        f"({self.event[OnOff.DICT_CHECK_DATE_YYYYMMDD].strftime('%Y/%m/%d')})")        


  @abstractmethod
  def _is_running(self, check_date) -> bool:
    '''
    起動判断
    - Returns
      - true: 起動すべき時
      - false: 起動すべきではない時     
    '''
    pass

  @abstractmethod
  def _on(self):
    '''
    起動メソッド
    '''
    pass


  @abstractmethod
  def _off(self):
    '''
    停止メソッド
    '''
    pass
