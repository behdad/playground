#include <stdint.h>
#include <assert.h>
#include <map>
#include <vector>
#include <string>
#include <iostream>

class token_t
{
  public:
  token_t () : value(0) {}
  token_t (const token_t &other) : value(other.value) {}
  unsigned int bytelen() const { return value & 0xFFu; }
  unsigned int firstbyte() const { return (value>>8) & 0xFFu; }
  private:
  friend class token_factory_t;
  explicit token_t (uint32_t value_) : value(value_) {}
  uint32_t value;
};

class token_factory_t
{
  token_factory_t () : quark_map(), quark_unmap() {}

  token_t from_string (const std::string &str)
  {
    unsigned int len = str.size ();
    assert (len > 0);
    assert (len < 256);
    if (len < 4)
    {
      uint32_t v = 0;
      for (int i = len - 1; i >= 0; i--)
	v = (v<<8) | str[i];
      v = (v<<8) | len;
      return token_t (v);
    }
    else
    {
      uint16_t q = quark_from_string (std::string (str, 1));
      uint32_t v = (uint32_t(q)<<16) | (uint32_t(str[0])<<8) | len;
      return token_t (v);
    }
  }

  std::string to_string (token_t tok) const
  {
    unsigned int len = tok.bytelen();
    uint32_t v = tok.value;
    if (len < 4)
    {
      char buf[3];
      for (unsigned int i = 0; i < len; i++)
      {
        v >>= 8;
	buf[i] = v&0xFFu;
      }
      return std::string(buf, len);
    }
    else
    {
      uint16_t q = v>>16;
      char firstbyte = v>>8;
      std::string str;
      str.push_back(firstbyte);
      str.append(quark_to_string(q));
      return str;
    }
  }

  private:
  //XXX make uncopyable properly

  uint16_t quark_from_string (const std::string &str)
  {
    auto qq = quark_map.find(str);
    if (qq != quark_map.end())
      return (*qq).second;
    uint16_t q = quark_unmap.size();
    quark_map[str] = q;
    quark_unmap.push_back(str);
    assert(q <= 0xFFFFu);
    return q;
  }
  std::string quark_to_string (uint16_t q) const
  {
    assert(q < quark_unmap.size());
    return quark_unmap[q];
  }
  std::map<std::string, uint16_t> quark_map;
  std::vector<std::string> quark_unmap;
};

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

