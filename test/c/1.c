typedef struct State State;
struct State {
    int c;
    State *out;
    State *out1;
    int lastlist;
};