#include <stdint.h>
#include <assert.h>
#include <map>
#include <vector>
#include <string>

class token_t
{
  typedef uint32_t int_type;

  token_t (int_type value_ = 0) : value(value_) {}
  token_t (token_t &other) : value(other.value) {}
  token_t (const std::string &str)
  {
    unsigned int len = str.size ();
    assert (len < 256);
    if (len < int_size)
    {
      unsigned int i = 0;
      int_type v = len;
      while (i++ < len)
      {
	v <<= 8;
	v |= str[i];
      }
      v <<= 8 * (int_size - len - 1);
      value = v;
    }
    else
    {
      assert (false); // Not implemented
    }
  }

  private:
  static const unsigned int int_size = sizeof (int_type);
  int_type value;
};
