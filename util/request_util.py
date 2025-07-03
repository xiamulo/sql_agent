def get_headers(header_raw):
  """
  通过原生请求头获取请求头字典
  :param header_raw: {str} 浏览器请求头
  :return: {dict} headers
  """
  return dict(line.split(": ", 1) for line in header_raw.split("\n"))