library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity top_level is
    port (
        MAX10_CLK1_50 : in std_logic;
        SW  : in std_logic_vector(9 downto 0);
        KEY : in std_logic_vector(1 downto 0);
        --------------------------------------------------
        -- Output
        --------------------------------------------------
        LED         : out std_logic_vector(9 downto 0)  := (others => '0');
        ARDUINO_IO  : out std_logic_vector(15 downto 0) := (others => '0')
    );
end top_level;

architecture rtl of top_level is

    --------------------------------------------------
    -- Registers
    --------------------------------------------------
    signal counter_reg  : std_logic_vector(31 downto 0) := (others => '0');
    signal glitch_reg   : std_logic                     := '0';
    signal clk          : std_logic;

    --------------------------------------------------
    -- Create state machine
    --------------------------------------------------
    type t_state is (IDLE, GLITCH, HOLDOFF);
    signal state : t_state := IDLE;

    --------------------------------------------------
    -- Constants
    --------------------------------------------------
    constant C_HOLD_TIME : std_logic_vector(31 downto 0) := std_logic_vector(to_unsigned(10000000, 32));

begin

    -- Combinatorical logic
    clk <= MAX10_CLK1_50;
    ARDUINO_IO(0) <= glitch_reg;

    MAIN_PROC : process(clk)

        variable v_led_reg : std_logic_vector(9 downto 0);
        variable v_counter_reg : std_logic_vector(31 downto 0);
        variable v_glitch_reg : std_logic;

    begin

        if rising_edge(clk) then

            -- Initialize variables
            v_led_reg       := (others => '0');
            v_counter_reg   := (others => '0');
            v_glitch_reg    := '1';
            
            --------------------------------------------------
            -- State machine
            --------------------------------------------------
            case state is 
                --------------------------------------------------
                when IDLE =>
                    --------------------------------------------------
                    v_led_reg(1 downto 0) := "11";

                    if (KEY(0) = '0') then
                        state <= GLITCH;
                    end if;

                --------------------------------------------------
                when GLITCH =>
                    -- Set glitch signal to low to turn off power
                    --------------------------------------------------
                    v_glitch_reg := '0';
                    
                    if (counter_reg(9 downto 0) >= SW) then
                        state <= HOLDOFF;
                        -- Will also set counter to 0
                    else
                        v_counter_reg := std_logic_vector(unsigned(counter_reg) + 1);
                    end if;

                --------------------------------------------------
                when HOLDOFF =>
                    -- This state is basically a debounce for the button press
                    --------------------------------------------------
                    v_led_reg(1 downto 0) := "10";

                    if (counter_reg >= C_HOLD_TIME) then
                        state <= IDLE;
                    else
                        v_counter_reg := std_logic_vector(unsigned(counter_reg) + 1);
                    end if;

            end case;
            
            -- Assign variables to signals
            LED             <= v_led_reg;
            counter_reg     <= v_counter_reg;
            glitch_reg      <= v_glitch_reg;

        end if;
        
    end process;

end architecture;