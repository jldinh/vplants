class Model {
    protected:
        // time of the simulation
        float time; 
 
    public:
        // run the model
        void run();
        // returns the time
        inline float get_time(){ return this->time; };
        // sets the time
        inline void set_time( float time ){ this->time=time; };
};
