
TARGET=raw_to_syx

CC=gcc

CFLAGS= -Wall -Wno-unused-value -Wno-unused-function

CFLAGS += -DAR_DEBUG

EXE_OBJ= \
	raw_to_syx.o

LIB_OBJ= \
	../libanalogrytm/pattern.o \
	../libanalogrytm/sysex.o

OBJ= \
	$(LIB_OBJ) \
	$(EXE_OBJ)


$(TARGET): $(OBJ)
	$(CC) $(OBJ) -o $(TARGET)

.c.o:
	$(CC) -c $< $(CFLAGS) -o $@

clean:
	rm -f $(OBJ) $(TARGET)


