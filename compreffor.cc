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
  uint8_t c[2];
  std::cin.read ((char *) c, 2);
  num_glyphs = (c[0]<<8)|c[1];
  assert (num_glyphs > 0);
  std::cin.read ((char *) c, 1);
  off_size = c[0];
  assert (off_size > 0);
  assert (off_size <= 4);
  std::vector<uint32_t> offsets;
  for (unsigned int i = 0; i < num_glyphs + 1; i++)
  {
    uint32_t offset = 0;
    for (unsigned int j = 0; j < off_size; j++)
    {
      uint8_t c;
      std::cin.get ((char &) c);
      offset = (offset<<8)|c;
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

  std::cout << "Read " << num_glyphs << " glyphs in " << offsets[num_glyphs] << " bytes\n";

  return 0;
}

