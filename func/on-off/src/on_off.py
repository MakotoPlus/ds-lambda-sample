import copy
import datetime
from abc import ABCMeta, abstractmethod

class OnOff(metaclass=ABCMeta):
  DICT_SWITCH_KEY = 'switch'
  DICT_CHECK_DATE_YYYYMMDD = 'check_date_yyyymmdd'
  SWITCH_ON = 'on'
  SWITCH_OFF = 'off'

  def __init__(self, event):
    self.event = self._check_event_dict(event)
    self.event = self._set_date(self.event)


  def _check_event_dict(self, event) -> dict:
    if not (OnOff.DICT_SWITCH_KEY in event ):
      raise Exception(f'event parameter key is not key:{OnOff.DICT_SWITCH_KEY}')

    switch_value = event[OnOff.DICT_SWITCH_KEY]
    if OnOff.SWITCH_ON != switch_value and OnOff.SWITCH_OFF != switch_value:
      raise Exception(f'event parameter value error {switch_value}')
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
      result = self._is_running(self.event[OnOff.DICT_CHECK_DATE_YYYYMMDD])
      if False == result:
        return
    if self.event[OnOff.DICT_SWITCH_KEY] == OnOff.SWITCH_ON:
      return self._on()
    else:
      return self._off()


  def _is_running(self, check_date) -> bool:
    '''
    起動判断
    - Returns
      - true: 起動すべき時
      - false: 起動すべきではない時     
    '''
    weekday = check_date.weekday()
    if (weekday == 5 ) or (weekday == 6):
      print(f"本日は、土,日なのでお休みです({check_date.strftime('%Y/%m/%d')})")
      return False
    return True


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
