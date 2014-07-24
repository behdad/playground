
CXXFLAGS = -std=c++11

%: %.cc
	c++ $< -o $@ $(CXXFLAGS)

all: compreffor
clean:
	rm -f compreffor
