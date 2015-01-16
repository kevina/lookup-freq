def options(opt):
  opt.load('compiler_cxx')

def configure(conf):
  #conf.env.CXX = '/opt/llvm/bin/clang++'
  conf.env.CXX = '/opt/gcc/bin/g++-4.9'
  conf.env.LINKFLAGS = ['-Wl,-rpath,/opt/gcc/lib64']
  conf.env.CXXFLAGS = ['-std=gnu++14','-Wall','-Wno-narrowing','-O2','-Wno-missing-braces']
  conf.load('compiler_cxx')

def noop(tsk):
    pass

def build(bld):
  bld.objects(source="common.cpp", target="common")

  bld.program(use="common", source="dump.cpp", target="dump")

  def gen(prog, **args):
      bld.program(use="common", source=prog+".cpp", target=prog)
      bld(name="do-"+prog, source=prog, rule = noop)
      bld(after="do-"+prog, **args)
 
  gen("import",
      rule="zcat /aux/ngrams/data/googlebooks-eng-all-1gram-20120701-*.gz | ./import",
      #rule="zcat /aux/ngrams/data/googlebooks-eng-all-1gram-20120701-q.gz | ./import",
      target="Freqs.dat FreqsPos.dat PosTotals.dat Totals.dat WordLookup.dat words.dat")

  bld(rule="sqlite3 /home/kevina/wordlist/git/scowl/scowl.db < ${SRC}",
      source="speller-export.sql",
      target="speller.tab")

  gen("import_speller",
      rule="./import_speller",
      source="WordLookup.dat words.dat speller.tab",
      target="SpellerLookup.dat words_w_speller.dat Speller.dat")

  gen("normalize",
      rule="./normalize", 
      #source="WordLookup.dat words.dat",
      source="SpellerLookup.dat words_w_speller.dat",
      target="ToLower.dat LowerLookup.dat words_w_lower.dat")

  gen("normalize_speller",
      rule="./normalize_speller",
      source="Speller.dat ToLower.dat",
      target="SpellerLower.dat")

  gen("tally_freqs_excl",
      rule="./tally_freqs_excl", 
      source="FreqsPos.dat",
      target="FreqsExclude.dat")
  
  gen("filter_freqs",
      rule="./filter_freqs",
      source="Freqs.dat FreqsExclude.dat ToLower.dat",
      target="FreqsFiltered.dat Counted.dat")

  gen("gather",
      rule="./gather",
      source="FreqsFiltered.dat Counted.dat ToLower.dat LowerLookup.dat",
      target="FreqAllLower.dat FreqRecentLower.dat FreqAllFiltered.dat FreqRecentFiltered.dat")

  gen("stats",
      rule="./stats", 
      source=("Speller.dat SpellerLower.dat " + 
              "SpellerLookup.dat LowerLookup.dat words_w_lower.dat " +
              "FreqAllFiltered.dat  FreqAllLower.dat  FreqRecentFiltered.dat  FreqRecentLower.dat "),
      target="StatsAllFiltered.dat  StatsAllLower.dat  StatsRecentFiltered.dat  StatsRecentLower.dat")

  gen("report",
      rule="true")
 
      
  