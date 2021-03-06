#ifndef CalibTracker_SiStripESProducers_Phase2TrackerCablingESProducer_H
#define CalibTracker_SiStripESProducers_Phase2TrackerCablingESProducer_H

#include "FWCore/Framework/interface/ESProducer.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "boost/cstdint.hpp"
#include <memory>

class Phase2TrackerCabling;
class Phase2TrackerCablingRcd;

class Phase2TrackerCablingESProducer : public edm::ESProducer {
  
 public:
  
  Phase2TrackerCablingESProducer( const edm::ParameterSet& );
  virtual ~Phase2TrackerCablingESProducer();
  
  virtual std::unique_ptr<Phase2TrackerCabling> produce( const Phase2TrackerCablingRcd& );
  
 private:
  
  Phase2TrackerCablingESProducer( const Phase2TrackerCablingESProducer& );
  const Phase2TrackerCablingESProducer& operator=( const Phase2TrackerCablingESProducer& );
  
  virtual Phase2TrackerCabling* make( const Phase2TrackerCablingRcd& ) = 0; 
  
};

#endif // CalibTracker_SiStripESProducers_Phase2TrackerCablingESProducer_H

