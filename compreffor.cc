#include <stdint.h>
#include <assert.h>
#include <map>
#include <vector>
#include <string>
#include <iostream>

class token_t
{
  typedef uint32_t int_type;

  token_t (int_type value_ = 0) : value(value_) {}
  token_t (token_t &other) : value(other.value) {}
  token_t (const std::string &str)
  {
    unsigned int len = str.size ();
    assert (len > 0);
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

  static inline unsigned int quark_for (const std::string &str)
  {
    return 0;
  }

  static unsigned int next_quark;
};

unsigned int token_t::next_quark = 0;

int
main (void)
{
  unsigned int num_glyphs, off_size;
  uint8_t c1, c0;
  std::cin >> c1 >> c0;
  num_glyphs = (c1<<8)|c0;
  assert (num_glyphs > 0);
  std::cin >> c0;
  off_size = c0;
  assert (off_size > 0);
  assert (off_size <= 4);
  std::vector<uint32_t> offsets;
  for (unsigned int i = 0; i < num_glyphs + 1; i++)
  {
    uint32_t offset = 0;
    for (unsigned int j = 0; j < off_size; j++)
    {
      std::cin.read ((char *) &c0, 1);
      offset = (offset<<8)|c0;
    }
    offsets.push_back (offset);
  }
  assert (offsets[0] == 1);
  std::string charstring;
  std::vector<std::string> charstrings;
  for (unsigned int i = 0; i < num_glyphs; i++)
  {
    assert (offsets[i] <= offsets[i+1]);
    unsigned int len = offsets[i+1] - offsets[i];
    assert (len);
    charstring.resize (len);
    std::cin.read (&charstring[0], len);
    charstrings.push_back (charstring);
  }

  return 0;
}

