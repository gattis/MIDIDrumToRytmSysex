import cstruct

NOTE_LENGTHS = range(2,32) + range(32,64,2) + range(64,128,4) + range(128,256,8) + range(256,512,16) + range(512,1024,32) + range(1024,2048,64) + [2048]
MIDI_TO_TRACK = {
    35:1,
    36:1,
    37:3,
    38:2,
    39:4,
    40:2,
    41:5,
    42:9,
    43:6,
    44:10,
    45:6,
    46:10,
    47:7,
    48:8,
    49:11,
    50:8,
    51:12,
    52:11,
    53:12,
    56:12
}

class Track(cstruct.CStruct):
    __byte_order__= cstruct.LITTLE_ENDIAN
    __struct__ = """
       unsigned short trigs[64];                  /* @0x0000..0x007F.  See AR_TRIG_xxx flags.                   */
       unsigned char notes[64];                   /* @0x0080..0x00BF.  0xFF=unset, MIDI note otherwise ((default is C-4 == 0x3C, 0x3B="-1", 0x3D="+1") */
       unsigned char velocities[64];              /* @0x00C0..0x00FF.  0xFF=unset, 0x00=0, 0x7F=127             */
       unsigned char note_lengths[64];            /* @0x0100..0x013F.  0=0.125, 1=0.188, 2=1/64, 3=0.313, 6=1/32, .., 126=128, 127=inf */
       signed char   micro_timings[64];           /* @0x0140..0x017F.  Micro timing (-23..+23) */
       unsigned char retrig_lengths[64];          /* @0x0180..0x01bF.  Retrig lengths (0..126(=128), 127=inf)   */
       unsigned char retrig_rates[64];            /* @0x01C0..0x01FF.  Retrig rates (0(=1/1)..16(=1/80))        */
       signed char   retrig_velocity_offsets[64]; /* @0x0200..0x023F.  Retrig velocity offsets (-128..+127)     */
       unsigned char trig_note;                   /* @0x0240           <void> trigNote                          */
       unsigned char trig_velocity;               /* @0x0241           <void> trigVelocity                      */
       unsigned char trig_note_length;            /* @0x0242           <void> trigLength                        */
       unsigned short trig_flags;                 /* @0x0243           <void> trigFlags                         */
       unsigned char __unknown2;                  /* @0x0245           <void> unknown                           */
       unsigned char num_steps;                   /* @0x0246           Number of steps (1..64)                  */
       unsigned char quantize_amount;             /* @0x0247           <void> quantizeAmount                    */
       unsigned char sound_locks[64];             /* @0x0248..0x0287   <void> soundLocks                        */
    """

class PLockSeq(cstruct.CStruct):
    __byte_order__= cstruct.LITTLE_ENDIAN
    __struct__ = """
       unsigned char plock_type;  /* @0x0000           0xFF=unused seq. See AR_PLOCK_TYPE_xxx               */
       unsigned char track_nr;    /* @0x0001           0xFF=unused seq. Tracknr (0..12)                     */
       unsigned char data[64];    /* @0x0002..0x0041.  Plock data (64 steps, value range is type dependent) */
    """

class Pattern(cstruct.CStruct):
    __byte_order__= cstruct.LITTLE_ENDIAN
    __struct__ = """
       unsigned char magic_header[4];  /* ??? a version number ??? reads '00 00 00 01' */
       struct Track  tracks[13];       /* @0x0004..0x20EB */
       struct PLockSeq plock_seqs[72]; /* @0x20EC..0x337B */
       unsigned char __unknown1;       /* @0x337C           Reads 0x00  */
       unsigned char pattern_len;      /* @0x337D           */
       unsigned char __unknown2;       /* @0x337E           Reads 0x00 */
       unsigned char __unknown3;       /* @0x337F           Reads 0x01 */
       unsigned char __unknown4;       /* @0x3380           Reads 0x00 - ITS KIT NUMBER! */
       unsigned char __unknown5;       /* @0x3381           Reads 0x00 7? 8?*/
       unsigned char __unknown6;       /* @0x3382           Reads 0x00, 0x01 to keep track lengths */
       unsigned char pattern_speed;    /* @0x3383           See AR_SPD_xxx. */
       unsigned char __unknown7;       /* @0x3384           Reads 0x00 */
       unsigned char __unknown8;       /* @0x3385           Reads 0x00 */
    """

def test():
    f = open("retest.raw","rb")
    pat = Pattern()
    data = f.read(len(pat))
    pat.unpack(data)
    print pat
    exit()



def tick_to_trig(tick,resolution):
    return int(round(tick / (resolution / 4.0)))

def ticklen_to_notelen(ticklen,resolution):
    min_diff,min_idx = (2048,127)
    norm_ticklen = ticklen/(resolution/4.)*16.0
    for idx,notelen in enumerate(NOTE_LENGTHS):
        diff = abs(norm_ticklen-notelen)
        if diff < min_diff:
            min_diff,min_idx = diff,idx
    return min_idx

def default_track():
    t = Track()
    t.trigs = [0]*64
    t.notes = [0xFF]*64
    t.velocities = [0xFF]*64
    t.note_lengths = [14]*64
    t.micro_timings = [0]*64
    t.retrig_lengths = [46]*64
    t.retrig_rates = [9]*64
    t.retrig_velocity_offsets = [0]*64
    t.trig_note = 0x3C
    t.trig_velocity = 127
    t.trig_note_length = 14
    t.trig_flags = 32775
    t.__unknown2 = 0
    t.num_steps = 16
    t.quantize_amount = 0
    t.sound_locks = [255]*64
    return t

def default_plockseq():
    pls = PLockSeq()
    pls.plock_type = 0xFF
    pls.track_nr = 0xFF
    pls.data = [0]*64
    return pls

def default_pattern():
    p = Pattern()
    p.magic_header = [0,0,0,1]
    p.tracks = [default_track() for i in xrange(13)]
    p.plock_seqs = [default_plockseq() for i in xrange(72)]
    p.__unknown1 = 0
    p.pattern_len = 64
    p.__unknown2 = 0
    p.__unknown3 = 1
    p.__unknown4 = 255
    p.__unknown5 = 0
    p.__unknown6 = 1
    p.pattern_speed = 2
    p.__unknown7 = 0
    p.__unknown8 = 0
    return p

import midi
def midi_to_rawsyx(infile):
    
    midipattern = midi.read_midifile(infile)
    if len(midipattern) != 1:
        print "WARN: expected only 1 track"
    midipattern.make_ticks_abs()

    syx = default_pattern()

    notes = {}
    for event in midipattern[0]:
        if type(event) in (midi.NoteOnEvent, midi.NoteOffEvent):
            notes.setdefault(event.pitch,[]).append(event)
        if type(event) == midi.EndOfTrackEvent:
            normlen = int(round(float(event.tick) / midipattern.resolution / 4.0)) * 16
            syx.pattern_len = normlen
            for track in syx.tracks:
                track.num_steps = normlen

    for note,events in notes.iteritems():
        i = 0
        trigs = [0]*64
        note_lengths = [0]*64
        velocities = [0]*64

        while i < len(events)-1:
            if type(events[i]) != midi.NoteOnEvent:
                print "WARN: Off event found before On event"
                i += 1
            elif type(events[i+1]) == midi.NoteOffEvent:
                trig = tick_to_trig(events[i].tick, midipattern.resolution)
                trigs[trig] = 37123
                ticklen = events[i+1].tick - events[i].tick
                note_lengths[trig] = ticklen_to_notelen(ticklen, midipattern.resolution)
                velocities[trig] = events[i].velocity
                i += 2
            else:
                trig = tick_to_trig(events[i].tick, midipattern.resolution)
                trigs[trig] = 37123
                note_lengths[trig] = 127
                velocities[trig] = events[i].velocity
                i += 1

        track = syx.tracks[MIDI_TO_TRACK[note]-1]
        track.trigs = trigs
        track.note_lengths = note_lengths
        track.velocities = velocities
        track.pack()

        out = open(infile+".raw",'wb')
        out.write(syx.pack())
        out.close()    

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test()
    fnames = sys.argv[1:]
    for fname in fnames:
        midi_to_rawsyx(fname)
